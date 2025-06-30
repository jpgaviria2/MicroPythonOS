from mpos.apps import Activity

import mpos.info
import sys

class About(Activity):

    def onCreate(self):
        screen = lv.obj()
        screen.set_style_border_width(0, 0)
        screen.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        screen.set_style_pad_all(mpos.ui.pct_of_display_width(2), 0)
        label1 = lv.label(screen)
        label1.set_text(f"MicroPythonOS version: {mpos.info.CURRENT_OS_VERSION}")
        label2 = lv.label(screen)
        label2.set_text(f"sys.version: {sys.version}")
        label3 = lv.label(screen)
        label3.set_text(f"sys.implementation: {sys.implementation}")
        label4 = lv.label(screen)
        label4.set_text(f"sys.platform: {sys.platform}")
        self.setContentView(screen)
