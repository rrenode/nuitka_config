from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Optional

from nuitka_config.utils.export_class import export
from nuitka_config.utils.platform_tools import pick_for_platform

from nuitka_config.serializers import (
    direct_serializer, 
    iterable_serializer, 
    bool_flag_serializer, 
    enum_serializer
)
    
#SECTION Python Controls
@export
class PyFlag(StrEnum):
    no_site = "-s"
    static_hashes = "static_hashes"
    no_warnings = "no_warnings"
    no_asserts = "no_asserts"
    no_docstrings = "no_docstrings"
    unbuffered = "-u"
    isolated = "isolated"
    package_mode = "-m"
    
@export
@dataclass
class PythonControls:
    #=================================================#
    # se debug version or not. 
    # Default uses what you are using to run Nuitka, most 
    #   likely a non-debug version.
    # Only for debugging and testing purposes.
    #=================================================#
    debug_build: bool | None = field(
        default=None,
        metadata={
            "serializer": bool_flag_serializer("python-debug")
        }
    )
    
    #=================================================# 
    # Python flags to use. 
    # Default is what you are using to run Nuitka, this enforces a specific mode. 
    # These are options that also exist to standard Python executable.
    # Currently supported: 
    #   "-S" (alias "no_site"), 
    #   "static_hashes" (do not use hash randomization), 
    #   "no_warnings" (do not give Python run time warnings),
    #   "-O" (alias "no_asserts"), 
    #   "no_docstrings" (do not use doc strings), 
    #   "-u" (alias "unbuffered"), 
    #   "isolated" (do not load outside code), 
    #   "-P" (alias "safe_path", do not used current directory in module search)
    #   "-m" (package mode, compile as "package.__main__")
    # Default empty.
    #=================================================#
    py_flags: list[PyFlag | str] = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("python-flag")
        }
    )
    
    #=================================================# 
    # Use static link library of Python. 
    # Allowed values are "yes", "no", and "auto" (when it's known to work).
    # Defaults to "auto".
    #=================================================#
    static_lib: str = field(
        default=None,
        metadata={
            "cli": "static-libpython"
        }
    )
#!SECTION    

#SECTION Package/Module Inclusion and Exclusion
@export
@dataclass
class Packages:
    #=================================================#
    # Include a whole package.
    # Give as a Python namespace, e.g. "some_package.sub_package" 
    #   and Nuitka will then find it and include it and all the 
    #   modules found below that disk location in the binary 
    #   or extension module it creates, and make it available 
    #   for import by the code. 
    # To avoid unwanted sub packages, e.g. test, you can do this:
    #   "--nofollow-import-to=*.tests"
    # Default empty.
    #=================================================#
    include_packages: list[str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("include-package")
        }
    )
    
    #=================================================#
    # Include a single module. 
    # Give as a Python namespace,  e.g. "some_package.some_module" 
    #   and Nuitka will then find it and include it in the 
    #   binary or extension module it creates, and make it available 
    #   for import by the code. 
    # Default empty.
    #=================================================#
    include_modules: list[str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("include-module")
        }
    )
    
    #=================================================#
    # Do not follow to that module name even if used, or 
    #   if a package name, to the whole package in any case, 
    #   overrides all other options. 
    # This can also contain patterns, e.g. "*.tests". 
    # Can be given multiple times.
    # Default empty.
    #=================================================#
    nofollow_import_to: list[str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("nofollow-import-to")
        }
    )
    
    #=================================================#
    # Descend into all imported modules. 
    # Defaults to on in standalone mode, otherwise off.
    #=================================================#
    follow_imports: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("follow-imports")
        }
    )
#!SECTION

#SECTION OneFile Options
@export
@dataclass
class OneFileControl:
    #=================================================#
    # Use this as a folder to unpack to in onefile mode.
    # Defaults to '{TEMP}/onefile_{PID}_{TIME}', 
    #   i.e. user temporary directory and being non-static it's removed.
    # Use e.g. a string like '{CACHE_DIR}/{COMPANY}/{PRODUCT}/{VERSION}'
    #   which is a good static cache path, this will then not be removed.
    #=================================================#
    temp_dir: str | None = field(
        default=None,
        metadata={
            "cli": "onefile-tempdir-spec"
        }
    )
    
    #=================================================#
    # This mode is inferred from your use of the spec. 
    # If it contains runtime dependent paths, "auto" resolves to 
    #   "temporary" which will make sure to remove the unpacked binaries 
    #   after execution, and cached will not remove it and see to 
    #   reuse its contents during next execution for faster startup times.
    #=================================================#
    cached_dir: str | None = field(
        default=None,
        metadata={
            "cli": "onefile-cache-mode"
        }
    )
    
    #=================================================#
    # When stopping the child, e.g. due to CTRL-C or shutdown or likewise
    #   the Python code gets a "KeyboardInterrupt", that it may handle to 
    #   for example, flush data. 
    # This is the amount of time in ms, before the child is killed in the hard way.
    # Unit is ms, and default 5000.
    #=================================================#
    grace_time_ms: int = field(
        default=5000,
        metadata={
            "cli": "onefile-child-grace-time"
        }
    )
    
    #=================================================# 
    # When creating the onefile, disable compression of the payload. 
    # This is mostly for debug purposes, or to save time. 
    # Default is off.
    #=================================================#
    no_compression: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("onefile-no-compression")
        }
    )
    
    #=================================================#
    # When creating the onefile, use an archive format, 
    #   that can be unpacked with "nuitka-onefile-unpack" rather than 
    #   a stream that only the onefile program itself unpacks. 
    # Default is off.
    #=================================================#
    as_archive: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("onefile-as-archive")
        }
    )
    
    #=================================================#
    # When creating the onefile, some platforms 
    #   (Windows currently, if not using a cached location) default to 
    #   using DLL rather than an executable for the Python code. 
    # This makes it use an executable in the unpacked files as well. 
    # Default is off.
    #=================================================#
    no_dll: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("onefile-no-dll")
        }
    )
#!SECTION
    
    
#SECTION Data Files
@export
@dataclass
class DataFiles:
    #=================================================#
    # Include data files for the given package name. 
    # DLLs and extension modules are not data files and 
    #   never included like this. 
    # Can use patterns the filenames as indicated below. 
    # Data files of packages are not included by default, but 
    #   package configuration can do it. 
    # This will only include non-DLL, non-extension modules, 
    #   i.e. actual data files. 
    # After a ":" optionally a filename pattern can be given as well,
    #   selecting only matching files. 
    # Examples: 
    #   "--include-package-data=package_name" (all files) 
    #   "--include-package-data=package_name:*.txt" (only certain type) 
    #   "--include-package-data=package_name:some_filename.dat(concrete file) 
    # Default empty.
    #=================================================#
    include_package_data: list[Path] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("include-package-data")
        }
    )
    
    #=================================================#
    # Include data files by filenames in the distribution.
    # There are many allowed forms. 
    # With '--include-data- files=/path/to/file/*.txt=folder_name/some.txt' 
    #   it will copy a single file and complain if it's multiple.
    # With '--include-data-files=/path/to/files/*.txt=folder_name/' 
    #   it will put all matching files into that folder. 
    # For recursive copy there is a form with 3 values that 
    #   '--include-data-files=/path/to/scan=folder_name/=**/*.txt' 
    # that will preserve directory structure. 
    # Default empty.
    #=================================================#
    include_data_files: list[Path] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("include-data-files")
        }
    )
    
    #=================================================#
    # Include data files from complete directory in the distribution. 
    # This is recursive. 
    # Check '--include-data-files' with patterns if you want non-recursive inclusion. 
    # An example would be '--include-data-dir=/path/some_dir=data/some_dir' 
    #   for plain copy, of the whole directory. All non-code files are copied, if 
    #       you want to use '--noinclude-data-files' option to remove them. 
    # Default empty.
    #=================================================#
    include_data_dirs: list[Path] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("include-data-dir")
        }
    )
    
    #=================================================#
    # Do not include data files matching the filename pattern given. 
    # This is against the target filename, not source paths. 
    # So to ignore a file pattern from package data for 'package_name' 
    #   should be matched as 'package_name/*.txt'. Or for the whole directory 
    #   simply use 'package_name'.
    # Default empty.
    #=================================================#
    no_include_data_files: list[Path] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("noinclude-data-files")
        }
    )
    
    #=================================================#
    # Include the specified data file patterns outside of the 
    #   onefile binary, rather than on the inside. 
    # Makes only sense in case of '--onefile' compilation. 
    # First files have to be specified as included with other 
    #   `--include-*data*` options, and then this refers to 
    # target paths inside the distribution. 
    # Default empty.
    #=================================================#
    include_onefile_external_data: list[Path] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("include-onefile-external-data")
        }
    )
#!SECTION

#SECTION DLL Files
@export
@dataclass
class DLLFileControl:
    #=================================================#
    # Do not include DLL files matching the filename pattern given. 
    # This is against the target filename, not source paths. 
    # So ignore a DLL 'someDLL' contained in the package 'package_name' 
    #   it should be matched as 'package_name/someDLL.*'. 
    # Default empty.
    #=================================================#
    noinclude_dlls: list[str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("noinclude-dlls")
        }
    )
#!SECTION

#SECTION Nuitka Warnings Control
@export
@dataclass
class NuitkaWarningControl:
    #=================================================#
    # Enable warnings for implicit exceptions detected at compile time.
    #=================================================#
    warn_implicit_exceptions: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("warn-implicit-exceptions")
        }
    )
    
    #=================================================#
    # Enable warnings for unusual code detected at compile time.
    #=================================================#
    warn_unusual_code: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("warn-unusual-code")
        }
    )
    
    #=================================================#
    # Allow Nuitka, on Windows, to download external code if necessary such as:
    #   - dependency walker, 
    #   - ccache, 
    #   - and even gcc. 
    # To disable, redirect input from nul device, 
    #   e.g. "</dev/null" or "<NUL:". 
    # Default is to prompt (FALSE).
    #=================================================#
    assume_yes_for_downloads: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("assume-yes-for-downloads")
        }
    )
#!SECTION

#SECTION Post-Compilation
@export
@dataclass
class PostCompilation:
    #=================================================#
    # Execute immediately the created binary (or import the compiled module). 
    # Defaults to off.
    #=================================================#
    run: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("run")
        }
    )
    
    #=================================================#
    # Execute inside a debugger, e.g. "gdb" or "lldb" to 
    #   automatically get a stack trace. 
    # The debugger is automatically chosen unless specified by 
    #   name with the NUITKA_DEBUGGER_CHOICE environment variable. 
    # Defaults to off.
    #=================================================#
    debugger: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("debugger")
        }
    )
    
#!SECTION

#SECTION Output Choices
@export
@dataclass
class OutputChoices:
    #=================================================#
    # Specify how the executable should be named. 
    # For extension modules there is no choice, also not for 
    #   standalone mode and using it will be an error. 
    # This may include path information that needs to exist though. 
    # Defaults to '<program_name>.exe' on this platform.
    #=================================================#
    file_name: str | None = field(
        default=None,
        metadata={
            "cli": "output-filename"
        }
    )
    
    #=================================================#
    # Specify where intermediate and final output files should be put. 
    # The DIRECTORY will be populated with 
    #   - build folder, 
    #   - dist folder, 
    #   - binaries, 
    #   - etc. 
    # Defaults to current directory.
    #=================================================#
    output_dir: Path | None = field(
        default=None,
        metadata={
            "cli": "output-dir"
        }
    )
    
    #=================================================#
    # Removes the build directory after producing the module or exe file. 
    # Defaults to off.
    #=================================================#
    remove_output: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("remove-output")
        }
    )
    
    #=================================================#
    # Do not create a '.pyi' file for extension modules created by Nuitka. 
    # This is used to detect implicit imports. 
    # Defaults to off.
    #=================================================#
    no_pyi_file: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("no-pyi-file")
        }
    )
    
    #=================================================#
    # Do not use stubgen when creating a '.pyi' file for extension 
    #   modules created by Nuitka. 
    # They expose your API, but stubgen may cause issues. 
    # Defaults to off.
    #=================================================#
    no_pyi_stubs: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("no-pyi-stubs")
        }
    )
#!SECTION

#SECTION Deployment Control
@export
@dataclass
class DeploymentControl:
    #=================================================#
    # Disable code aimed at making finding compatibility issues easier. 
    # This will for e.g. prevent execution with "-c" argument, 
    #   which is often used by code that attempts run a module, 
    #   and causes a program to start itself over and over potentially.
    # Disable once you deploy to end users, for finding typical issues, this
    #   is very helpful during development. 
    # Default off.
    #=================================================#
    deployment: str | None = field(
        default=None,
        metadata={
            "cli": "deployment"
        }
    )
    
    #TODO NoDeploymentFlag
    no_deployment_flag = None
#!SECTION

#SECTION Environment Control
@export
@dataclass
class EnvControl:
    #=================================================#
    # Force an environment variables to a given value.
    # Default empty.
    #=================================================#
    force_envs: list[str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("force-runtime-environment-variable")
        }
    )
#!SECTION

#SECTION Debug Features
@export
@dataclass
class Debug:
    """Debug symbols and runtime tracing.
    """
    #=================================================#
    # Executing all self checks possible to find errors in Nuitka.
    # Do not use for production. 
    # Defaults to off.
    #=================================================#
    debug: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("debug")
        }
    )
    
    #=================================================#
    # Disable check normally done with "--debug". 
    # The C compilation may produce warnings, which it often does 
    #   for some packages without these being issues, esp. for unused values.
    #=================================================#
    disable_c_warnings: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("no-debug-c-warnings")
        }
    )
    
    #=================================================#
    # Keep debug info in the resulting object file for better 
    #   debugger interaction. 
    # Defaults to off.
    #=================================================#
    unstripped: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("unstripped")
        }
    )
    
    #=================================================#
    # Traced execution output, output the line of code 
    #   before executing it. 
    # Defaults to off.
    #=================================================#
    trace_execution: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("trace-execution")
        }
    )
    
    #=================================================#
    # Write the internal program structure, result of 
    #   optimization in XML form to given filename.
    #=================================================#
    xml: Path | None = field(
        default=None,
        metadata={
            "cli": "xml"
        }
    )
    
    #=================================================#
    # Attempt to use less memory, by forking less C compilation 
    #   jobs and using options that use less memory. 
    # For use on embedded machines. 
    # Use this in case of out of memory problems.
    # Defaults to off.
    #=================================================#
    low_memory: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("low-memory")
        }
    )
#!SECTION

#SECTION CacheControl
@export
class CacheChoice(StrEnum):
    all = "all"
    ccache = "ccache"
    bytecode = "bytecode"
    compression = "compression"
    dll_dependencies = "dll-dependencies"

@export
@dataclass
class CacheControl:
    #=================================================#
    # Disable selected caches, specify "all" for all cached.
    # Default none.
    #=================================================#
    disable_caches: list[CacheChoice | str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("disable-cache")
        }
    )
    
    #=================================================#
    # Clean the given caches before executing, specify "all" for all cached.
    # Default none.
    #=================================================#
    clean_cache: list[CacheChoice | str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("clean-cache")
        }
    )
#!SECTION

#SECTION Tracing/Logging
@export
@dataclass
class TracingFeatures:
    #=================================================#
    # Report module, data files, compilation, plugin, etc
    #   details in an XML output file. 
    # This is also super useful for issue reporting. 
    # These reports can be used to re-create the environment 
    #   easily using it with '--create-environment-from-report', 
    #   but contain a lot of information. 
    # Default is off.
    #=================================================#
    report_filename: str | None = field(
        default=None,
        metadata={
            "cli": "report"
        }
    )
    
    #=================================================#
    # Report data in diffable form, i.e. no timing or memory 
    #   usage values that vary from run to run. 
    # Default is off.
    #=================================================#
    report_diffable: str | None = field(
        default=None,
        metadata={
            "cli": "report-diffable"
        }
    )
    
    # TODO - ReportUserProvided
    report_user_provided = None
    
    # TODO - ReportTemplate
    report_template = None
    
    #=================================================#
    # Disable all information outputs, but show warnings.
    # Defaults to off.
    #=================================================#
    quiet: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("quiet")
        }
    )
    
    #=================================================#
    # Run the C building backend Scons with verbose information, 
    #   showing the executed commands, detected compilers. 
    # Defaults to off.
    #=================================================#
    show_scons: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("show-scons")
        }
    )
    
    #=================================================#
    # Disable progress bars. 
    # Defaults to off.
    #=================================================#
    no_progressbar: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("no-progressbar")
        }
    )
    
    #=================================================#
    # Provide memory information and statistics. 
    # Defaults to off.
    #=================================================#
    show_memory: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("show-memory")
        }
    )
    
    #=================================================#
    # Where to output '--report', should be a filename. 
    # Default is standard output.
    #=================================================#
    show_modules_output: Path | None = field(
        default=None,
        metadata={
            "cli": "show-modules-output"
        }
    )
    
    #=================================================# 
    # Output details of actions taken, esp. in optimizations. 
    # Can become a lot. 
    # Defaults to off.
    #=================================================#
    verbose: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("verbose")
        }
    )
    
    #=================================================# 
    # Where to output from '--verbose', should be a filename. 
    # Default is standard output.
    #=================================================#
    verbose_output: Path | None = field(
        default=None,
        metadata={
            "cli": "verbose-output"
        }
    )
#!SECTION

#SECTION OS Controls
#SECTION WindowsOSControls
@export
class WindowsConsoleMode(StrEnum):
    # creates a console window unless the program was started from one.
    force = "force"
    
    # With 'disable' it doesn't create or use a console at all.
    disable = "disable"
    
    # With 'attach' an existing console will be used for outputs.
    attach = "attach"
    
    # With 'hide' a newly spawned console will be hidden and an already
    #   existing console will behave like 'force'. 
    hide = "hide"

@export
@dataclass
class WindowsOSControl:
    # Select console mode to use. Default mode is 'force'.
    console_mode: WindowsConsoleMode = field(
        default=WindowsConsoleMode.force,
        metadata={
            "serializer": enum_serializer("windows-console-mode")
        }
    )
    
    # Add executable icon. Can be given multiple times for different 
    #   resolutions or files with multiple icons inside.
    icon_from_ico: Path | None = field(
        default=None,
        metadata={
            "cli": "windows-icon-from-ico"
        }
    )
    
    # Copy executable icons from this existing executable (Windows only).
    icon_from_exe: Path | None = field(
        default=None,
        metadata={
            "cli": "windows-icon-from-exe"
        }
    )
    
    # When compiling for Windows and onefile, show this
    #   while loading the application. Defaults to off.
    slash_screen: str | None = field(
        default=None,
        metadata={
            "cli": "onefile-windows-splash-screen"
        }
    )
    
    # Request Windows User Control, to grant admin rights on
    #   execution. (Windows only). Defaults to off.
    uac_admin: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("windows-uac-admin")
        }
    )
    
    # Request Windows User Control, to enforce running from 
    #   a few folders only, remote desktop access. 
    #   (Windows only). Defaults to off.
    uac_uiaccess: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("windows-uac-uiaccess")
        }
    )
#!SECTION

#SECTION MacOSControls
@export
class MacArchTarget(StrEnum):
    limit = "limit"
    native = "native"

@export
class MacAppMode(StrEnum):
    gui = "gui"
    ui_element = "ui-element"
    background = "background"

@export
class MacMultipleInstance(StrEnum):
    off = "off"
    prevent = "LSMultipleInstancesProhibited"

@export
@dataclass
class MacOSControls:
    #=================================================#
    #When compiling for macOS, create a bundle rather than
    #   a plain binary application. 
    # This is the only way to unlock the disabling of console, 
    #   get high DPI graphics, etc. and implies standalone mode. 
    # Defaults to off.
    #=================================================#
    create_app_bundle: bool = field(
        default=False,
        metadata={
            "serializer": bool_flag_serializer("macos-create-app-bundle")
        }
    )
    
    #=================================================#
    # What architectures is this to supposed to run on.
    # Default and limit is what the running Python allows for. 
    # Default is "native" which is the architecture the Python is run with.
    #=================================================#
    target_arch: MacArchTarget = field(
        default=MacArchTarget.native,
        metadata={
            "serializer": enum_serializer("macos-target-arch")
        }
    )
    
    #=================================================#
    # Add icon for the application bundle to use. 
    # Can be given only one time. 
    # Defaults to Python icon if available.
    #=================================================#
    app_icon: Path | None = field(
        default=None,
        metadata={
            "cli": "macos-app-icon"
        }
    )
    
    #=================================================#
    # Name of the application to use for macOS signing.
    # Follow "com.YourCompany.AppName" naming results for 
    #   best results, as these have to be globally unique,
    #   and will potentially grant protected API accesses.
    #=================================================#
    signed_app_name: str | None = field(
        default=None,
        metadata={
            "cli": "macos-signed-app-name"
        }
    )
    
    #=================================================#
    # Name of the product to use in macOS bundle information. 
    # Defaults to base filename of the binary.
    #=================================================#
    app_name: str | None = field(
        default=None,
        metadata={
            "cli": "macos-app-name"
        }
    )
    
    #=================================================#
    # Mode of application for the application bundle. 
    # When launching a Window, and appearing in Docker is desired, 
    #   default value "gui" is a good fit. 
    # Without a Window ever, the application is a "background" application. 
    # For UI elements that get to display later, "ui-element" is in-between. 
    # The application will not appear in dock, but get full access to
    #   desktop when it does open a Window later.
    #=================================================#
    app_mode: MacAppMode = field(
        default=MacAppMode.gui,
        metadata={
            "serializer": enum_serializer("macos-app-mode")
        }
    )
    
    #=================================================#
    # For application bundles, set the flag "LSMultipleInstancesProhibited" 
    #   to prevent launching multiple instances of the application. 
    # Default is off.
    #=================================================#
    prohibit_multiple_instance: MacMultipleInstance | None = field(
        default=None,
        metadata={
            "serializer": enum_serializer("macos-prohibit-multiple-instances")
        }
    )
    
    #TODO - MacSignIdentity
    sign_identity = None
    
    #TODO - MacSignNotarization
    sign_notarization = None
    
    #=================================================#
    # Product version to use in macOS bundle information.
    # Defaults to "1.0" if not given.
    #=================================================#
    app_version: str | None = field(
        default=None,
        metadata={
            "cli": "macos-app-version"
        }
    )
    
    #TODO - MacProtectedResource
    # https://developer.apple.com/documentation/bundleresources/information_property_list/protected_resources
    protected_resource = None
#!SECTION

#SECTION LinuxOSControls
@export
@dataclass
class LinuxOSControls:
    icon_path: Path | None = field(
        default=None,
        metadata={
            "cli": "linux-icon"
        }
    )
#!SECTION

#SECTION OS Controls Dataclass
@export
@dataclass
class OSControls:
    #=================================================#
    #STUB - Ambiguous
    # Force standard output of the program to go to this location. 
    #  Useful for programs with disabled console and programs using 
    #   the Windows Services Plugin of Nuitka commercial. 
    # Defaults to not active, 
    #   use e.g. '{PROGRAM_BASE}.out.txt', i.e. file near your program.
    # Check User Manual for full list of available values.
    #=================================================#
    force_stdout: str | None = field(
        default=None,
        metadata={
            "cli": "force-stdout-spec"
        }
    )
    
    #=================================================#
    #STUB - Ambiguous
    # Force standard error of the program to go to this location. 
    # Useful for programs with disabled console and programs using 
    #   the Windows Services Plugin of Nuitka commercial. 
    # Defaults to not active, 
    #   use e.g. '{PROGRAM_BASE}.err.txt', i.e. file near your program.
    # Check User Manual for full list of available values.
    #=================================================#
    force_stderr: str | None = field(
        default=None,
        metadata={
            "cli": "force-stderr-spec"
        }
    )
    
    #=================================================#
    # Created as a proxy for this config builder.
    # Options are: WindowsOSControl | MacOSControls | LinuxOSControls
    # Defaults to default values of current os.
    #=================================================#
    os_specific: \
        WindowsOSControl | MacOSControls | LinuxOSControls | None = \
            field(
                default_factory=lambda: pick_for_platform(
                    windows_option=WindowsOSControl,
                    mac_option=MacOSControls,
                    linux_option=LinuxOSControls
                )()
            )
#!SECTION
#!SECTION

#SECTION BinaryVersionInfo
@export
@dataclass
class BinaryVersionInfo:
    #=================================================# 
    # Name of the company to use in version information.
    # Defaults to unused.
    #=================================================#
    company_name: str | None = field(
        default=None,
        metadata={
            "cli": "company-name"
        }
    )
    
    #=================================================#
    # Name of the product to use in version information.
    # Defaults to base filename of the binary.
    #=================================================#
    product_name: str | None = field(
        default=None,
        metadata={
            "cli": "product-name"
        }
    )
    
    #=================================================#
    # File version to use in version information. 
    # Must be a sequence of up to 4 numbers, e.g. 1.0 or 1.0.0.0, 
    #   no more digits are allowed, no strings are allowed.
    # Defaults to unused.
    #=================================================#
    file_version: str | None = field(
        default=None,
        metadata={
            "cli": "file-version"
        }
    )
    
    #=================================================#
    # Product version to use in version information. 
    # Same rules as for file version. Defaults to unused.
    #=================================================#
    product_version: str | None = field(
        default=None,
        metadata={
            "cli": "product-version"
        }
    )
    
    #=================================================#
    # Description of the file used in version information.
    # Windows only at this time. 
    # Defaults to binary filename.
    #=================================================#
    file_description: str | None = field(
        default=None,
        metadata={
            "cli": "file-description"
        }
    )
    
    #=================================================# 
    # Copyright used in version information. 
    # Windows/macOS only at this time. 
    # Defaults to not present.
    #=================================================#
    copyright_text: str | None = field(
        default=None,
        metadata={
            "cli": "copyright"
        }
    )
    
    #=================================================#
    # Trademark used in version information. 
    # Windows/macOS only at this time. 
    # Defaults to not present.
    #=================================================#
    trademark_text: str | None = field(
        default=None,
        metadata={
            "cli": "trademarks"
        }
    )
#!SECTION

#SECTION C Compiler Control

@export
class CompilerChoice(StrEnum):
    #=================================================#
    # Enforce the use of clang. 
    # On Windows this requires a working Visual Studio 
    #   version to piggy back on.
    # Defaults to off.
    #=================================================#
    clang = "clang"
    
    #=================================================#
    # Enforce the use of MinGW64 on Windows. 
    # Defaults to off unless MSYS2 with MinGW Python is used.
    #=================================================#
    mingw64 = "mingw64"
    
    #=================================================#
    # Enforce the use of specific MSVC version on Windows.
    # Allowed values are e.g. "14.3" (MSVC 2022) and other
    #   MSVC version numbers, specify "list" for a list of
    #   installed compilers, or use "latest".  
    # Defaults to latest MSVC being used if installed, 
    #   otherwise MinGW64 is used.
    #=================================================#
    msvc = "msvc"

@export
@dataclass
class LTOChoice(StrEnum):
    yes = "yes"
    no = "no"
    auto = "auto"

@export
@dataclass
class CCompilerControl:
    #=================================================#
    #=================================================#
    compiler: CompilerChoice | str | None = field(
    default=None,
    metadata={
        "serializer": direct_serializer()
    }
    )
     
    #=================================================#
    # Specify the allowed number of parallel C compiler jobs. 
    # Negative values are system CPU minus the given value. 
    # Defaults to the full system CPU count unless low memory mode 
    #   is activated, then it defaults to 1.
    #=================================================#
    jobs: int | None = field(
        default=None,
        metadata={
            "cli":"jobs"
        }
    )
    
    #=================================================#
    #Use link time optimizations (MSVC, gcc, clang). 
    # Allowed values are "yes", "no", and "auto" 
    #   (when it's known to work). 
    # Defaults to "auto".
    #=================================================#
    lto: LTOChoice = field(
        default_factory=lambda: LTOChoice.auto,
        metadata={
            "serializer": enum_serializer("lto")
        }
    )
#!SECTION

#SECTION Plugin Control
@export
@dataclass
class PluginControl:
    #=================================================#
    # Enabled plugins. 
    # Must be plug-in names. 
    # Use '--plugin-list' to query the full list and exit. 
    # Default empty.
    #=================================================#
    use_plugins: list[str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("enable-plugins")
        }
    )
    
    #=================================================#
    # Disabled plugins. 
    # Must be plug-in names. Use '--plugin-list' to query 
    #   the full list and exit. 
    # Most standard plugins are not a good idea to disable.
    # Default empty.
    #=================================================#
    disable_plugins: list[str] | None = field(
        default=None,
        metadata={
            "serializer": iterable_serializer("disable-plugins")
        }
    )
#!SECTION

#SECTION Full Config DataClass
  
@export
class BuildMode(StrEnum):
    #=================================================#
    # Creates a directory (dist/your_app/) containing:
    #   - Your app executable
    #   - All dependencies (Python DLL, packages, plugins, etc.)
    #   - Portable — but still a folder of files.
    #
    # Use this when you want a fully self-contained app that doesn't rely 
    #   on a system Python install.
    #=================================================#
    standalone = "standalone"
    
    #=================================================#
    # Builds on standalone, but compresses everything into a single .exe or binary.
    # - At runtime, it unpacks the contents into a temporary 
    #       directory and runs it from there.
    # - Slightly slower startup, but more portable.
    #
    # Use when you want a single-file app for easier distribution.
    # Implicitly sets standalone = true.
    #=================================================#
    onefile = "onefile"
    
    module = "module"
    
    default = "accelerated"
    
    dll = "NotImplementedError"
    
@export
@dataclass
class NuitkaConfig:
    entry_file: Path = field(
        default=Path("__main__.py")
    )
    build_mode: BuildMode = field(
        default=BuildMode.default
    )
    one_file_options: OneFileControl | None = None
    datas: DataFiles = field(default_factory=DataFiles)
    dlls: DLLFileControl = field(default_factory=DLLFileControl)
    packages: Packages = field(default_factory=Packages)
    python: PythonControls = field(default_factory=PythonControls)
    plugins: PluginControl = field(default_factory=PluginControl)
    compiler: CCompilerControl = field(default_factory=CCompilerControl)
    post_compile: PostCompilation = field(default_factory=PostCompilation)
    os: OSControls = field(default_factory=OSControls)
    binary_versioning: BinaryVersionInfo = field(default_factory=BinaryVersionInfo)
    output: OutputChoices = field(default_factory=OutputChoices)
    deployment: DeploymentControl = field(default_factory=DeploymentControl)
    env: EnvControl = field(default_factory=EnvControl)
    debug: Debug = field(default_factory=Debug)
    caching: CacheControl = field(default_factory=CacheControl)
    tracing: TracingFeatures = field(default_factory=TracingFeatures)
    nuk_warns: NuitkaWarningControl = field(default_factory=NuitkaWarningControl)
    extras: str | list[str] = field(default="")
#!SECTION