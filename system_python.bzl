load("@python_3_9//:version.bzl", "LINUX_AARCH64_SHA256", "LINUX_X86_64_SHA256", "MAC_ARM64_SHA256", "MAC_X86_64_SHA256", "WINDOWS_X86_64_SHA256", "python_info")

def _py_runtime_impl(rctx):
    rctx.file("BUILD.bazel", """
load("@rules_python//python:defs.bzl", "py_runtime")

py_runtime(
    name = "system_python",
    interpreter_path = "/usr/local/bin/python3",
    python_version = "PY3",
    visibility = ["//visibility:public"],
)
""")

system_python = repository_rule(
    implementation = _py_runtime_impl,
)