import sys, traceback
from datetime import datetime

from path_helpers import path
from flatland import Form, Float, Integer, Boolean, String
from flatland.validation import ValueAtLeast, ValueAtMost
from microdrop.logger import logger
from microdrop.plugin_helpers import (AppDataController, StepOptionsController,
                                      get_plugin_info)
from microdrop.plugin_manager import (PluginGlobals, Plugin, IPlugin,
                                      implements, emit_signal)
from microdrop.app_context import get_app
import gobject

PluginGlobals.push_env('microdrop.managed')


class SyringePumpPlugin(Plugin, AppDataController, StepOptionsController):
    """
    This class is automatically registered with the PluginManager.
    """
    implements(IPlugin)
    version = get_plugin_info(path(__file__).parent).version
    plugin_name = get_plugin_info(path(__file__).parent).plugin_name

    '''
    AppFields
    ---------

    A flatland Form specifying application options for the current plugin.
    Note that nested Form objects are not supported.

    Since we subclassed AppDataController, an API is available to access and
    modify these attributes.  This API also provides some nice features
    automatically:
        -all fields listed here will be included in the app options dialog
            (unless properties=dict(show_in_gui=False) is used)
        -the values of these fields will be stored persistently in the microdrop
            config file, in a section named after this plugin's name attribute
    '''
    AppFields = Form.of(
        Float.named('steps_per_microliter').using(optional=True, default=1.0),
        #Boolean.named('bool_field').using(optional=True, default=False),
        #String.named('string_field').using(optional=True, default=''),
    )

    '''
    StepFields
    ---------

    A flatland Form specifying the per step options for the current plugin.
    Note that nested Form objects are not supported.

    Since we subclassed StepOptionsController, an API is available to access and
    modify these attributes.  This API also provides some nice features
    automatically:
        -all fields listed here will be included in the protocol grid view
            (unless properties=dict(show_in_gui=False) is used)
        -the values of these fields will be stored persistently for each step
    '''
    StepFields = Form.of(
        Float.named('microliters_per_min').using(optional=True, default=100,
                                        validators=
                                        [ValueAtLeast(minimum=0),
                                         ValueAtMost(maximum=100000)]),
        Float.named('microliters').using(optional=True, default=10,
                                            #validators=
                                            #[ValueAtLeast(minimum=0),
                                            # ValueAtMost(maximum=100000)]
                                           ),
        #Boolean.named('bool_field').using(optional=True, default=False),
        #String.named('string_field').using(optional=True, default=''),
    )

    def __init__(self):
        self.name = self.plugin_name
        self.timeout_id = None
        self.start_time = None

    def on_step_run(self):
        """
        Handler called whenever a step is executed. Note that this signal
        is only emitted in realtime mode or if a protocol is running.

        Plugins that handle this signal must emit the on_step_complete
        signal once they have completed the step. The protocol controller
        will wait until all plugins have completed the current step before
        proceeding.

        return_value can be one of:
            None
            'Repeat' - repeat the step
            or 'Fail' - unrecoverable error (stop the protocol)
        """
        app = get_app()
        logger.info('[SyringePumpPlugin] on_step_run(): step #%d',
                    app.protocol.current_step_number)
        app_values = self.get_app_values()
        return_value = None
        emit_signal('on_step_complete', [self.name, return_value])

    def on_step_options_swapped(self, plugin, old_step_number, step_number):
        """
        Handler called when the step options are changed for a particular
        plugin.  This will, for example, allow for GUI elements to be
        updated based on step specified.

        Parameters:
            plugin : plugin instance for which the step options changed
            step_number : step number that the options changed for
        """
        pass

    def on_step_swapped(self, old_step_number, step_number):
        """
        Handler called when the current step is swapped.
        """
        pass


PluginGlobals.pop_env()
