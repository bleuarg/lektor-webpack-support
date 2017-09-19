import os

from lektor.pluginsystem import Plugin
from lektor.reporter import reporter
from lektor.utils import locate_executable, portable_popen


class WebpackSupportPlugin(Plugin):
    name = 'Webpack Support Plugin'
    description = 'Super simple plugin that runs a front-end tooling build or start command'

    def __init__(self, *args, **kwargs):
        Plugin.__init__(self, *args, **kwargs)
        self.node_process = None

    def on_env_setup(self, **extra):
        # todo: set default to 'frontend'
        frontend_source = self.get_config().get('frontend_source')
        frontend_root = os.path.join(self.env.root_path, frontend_source);
        self.env.jinja_env.globals['frontend_root'] = frontend_root
        self.env.jinja_env.globals['frontend_source'] = frontend_source

    def is_enabled(self, extra_flags):
        return bool(extra_flags.get('frontend'))

    def run_webpack(self, watch=False):
        # TODO load config from
        # https://www.getlektor.com/docs/api/plugins/plugin/get-config/
        # https://www.getlektor.com/docs/api/plugins/plugin/config-filename/
        frontend_root = self.env.jinja_env.globals.frontend_root
        args = []
        if watch:
            args.extend(('npm', 'start'))
        else
            args.extend(('npm', 'run', 'build'))
        return portable_popen(args, cwd=frontend_root)

    def install_node_dependencies(self):
        frontend_root = self.env.jinja_env.globals.frontend_root

        # Use yarn over npm if it's availabe and there is a yarn lockfile
        has_yarn_lockfile = os.path.exists(os.path.join(
            frontend_root, 'yarn.lock'))
        pkg_manager = 'npm'
        if locate_executable('yarn') is not None and has_yarn_lockfile:
            pkg_manager = 'yarn'

        reporter.report_generic('Running {} install'.format(pkg_manager))
        portable_popen([pkg_manager, 'install'], cwd=frontend_root).wait()

    def on_server_spawn(self, **extra):
        extra_flags = extra.get("extra_flags") or extra.get("build_flags") or {}
        if not self.is_enabled(extra_flags):
            return
        self.install_node_dependencies()
        reporter.report_generic('Spawning node watcher')
        self.node_process = self.run_webpack(watch=True)

    def on_server_stop(self, **extra):
        if self.node_process is not None:
            reporter.report_generic('Stopping webpack watcher')
            self.node_process.kill()

    def on_before_build_all(self, builder, **extra):
        extra_flags = getattr(
            builder, "extra_flags", getattr(builder, "build_flags", None)
        )
        if not self.is_enabled(extra_flags) \
           or self.node_process is not None:
            return
        self.install_node_dependencies()
        reporter.report_generic('Starting webpack build')
        self.run_webpack().wait()
        reporter.report_generic('Webpack build finished')
