"""Windows resource gate and watchdog; never terminates other applications."""

import ctypes
import json
import os
from pathlib import Path
import subprocess
import threading
from time import perf_counter

import psutil


class Memory(ctypes.Structure):
    _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
        (name, ctypes.c_ulonglong) for name in ("total", "available", "commit_total", "commit_available", "virtual_total", "virtual_available", "extended")]


def resource() -> dict:
    memory = Memory()
    memory.length = ctypes.sizeof(memory)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)):
        raise ctypes.WinError()
    info = psutil.Process().memory_info()
    return {"available_ram_bytes": memory.available, "commit_headroom_bytes": memory.commit_available,
            "memory_load_percent": memory.load, "process_rss_bytes": info.rss,
            "process_peak_working_set_bytes": info.peak_wset,
            "disk_free_bytes": {drive: psutil.disk_usage(drive).free for drive in ("C:/", "D:/")}}


def gpu_resource() -> dict:
    output = subprocess.check_output(["nvidia-smi", "--query-gpu=name,driver_version,memory.total,memory.used,memory.free", "--format=csv,noheader,nounits"], text=True, creationflags=0x08000000, timeout=10).strip().splitlines()
    if len(output) != 1:
        raise RuntimeError("This run requires exactly one declared GPU")
    name, driver, total, used, free = [value.strip() for value in output[0].split(",")]
    return {"name": name, "driver": driver, "total_mib": int(total), "used_mib": int(used), "free_mib": int(free)}


def unsafe(sample: dict, policy: dict) -> bool:
    return (sample["available_ram_bytes"] < policy["stop_available_ram_mib"] * 1024**2
            or sample["commit_headroom_bytes"] < policy["stop_commit_headroom_gib"] * 1024**3
            or sample["memory_load_percent"] >= policy["stop_memory_load_percent"])


def gate(sample: dict, gpu: dict, policy: dict, approved_low_memory: bool) -> None:
    if unsafe(sample, policy) or sample["disk_free_bytes"]["C:/"] < 10 * 1024**3 or sample["disk_free_bytes"]["D:/"] < 1024**3:
        raise RuntimeError("Unsafe RAM/commit/storage resource preflight")
    minimum = 5 if approved_low_memory else policy["recommended_available_ram_gib"]
    if sample["available_ram_bytes"] < minimum * 1024**3:
        raise RuntimeError(f"Available RAM below {minimum} GiB model-loading gate; no model loaded")
    if gpu["free_mib"] < 2000 or gpu["used_mib"] > 256:
        raise RuntimeError("GPU is busy or insufficient VRAM; do not load another model")


class Monitor:
    def __init__(self, policy: dict, directory: Path):
        self.policy, self.directory = policy, directory
        self.stop = threading.Event()
        self.summary = {"samples": 0, "peak_rss_bytes": 0, "peak_working_set_bytes": 0,
                        "min_available_ram_bytes": 2**64, "min_commit_headroom_bytes": 2**64,
                        "peak_device_used_mib": 0}
        self.thread = threading.Thread(target=self.watch, daemon=True)

    def sample(self):
        sample = resource()
        self.summary["samples"] += 1
        for output, value in (("peak_rss_bytes", sample["process_rss_bytes"]), ("peak_working_set_bytes", sample["process_peak_working_set_bytes"])):
            self.summary[output] = max(self.summary[output], value)
        for output, value in (("min_available_ram_bytes", sample["available_ram_bytes"]), ("min_commit_headroom_bytes", sample["commit_headroom_bytes"])):
            self.summary[output] = min(self.summary[output], value)
        return sample

    def watch(self):
        low_since, last_gpu = None, 0
        try:
            while not self.stop.is_set():
                sample, now = self.sample(), perf_counter()
                if unsafe(sample, self.policy):
                    low_since = now if low_since is None else low_since
                    if now - low_since >= self.policy["stop_sustained_seconds"]:
                        raise RuntimeError("Critical memory pressure sustained; stopped own run")
                else:
                    low_since = None
                if now - last_gpu >= self.policy["gpu_monitor_interval_seconds"]:
                    self.summary["peak_device_used_mib"] = max(self.summary["peak_device_used_mib"], gpu_resource()["used_mib"])
                    last_gpu = now
                self.stop.wait(self.policy["monitor_interval_seconds"])
        except BaseException as error:
            self.directory.mkdir(parents=True, exist_ok=True)
            (self.directory / "RESOURCE_STOP.json").write_text(json.dumps({"error": str(error), "resource": self.summary}), encoding="utf-8")
            os._exit(77)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop.set()
        self.thread.join(timeout=12)
        self.sample()
