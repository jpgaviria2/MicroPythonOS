import time

import mpos.config

# screens:
appscreen = lv.screen_active()
settings_screen = None




# Settings screen implementation
class SettingsScreen(lv.obj):
    def __init__(self):
        super().__init__(None)
        self.prefs = mpos.config.SharedPreferences("com.lightningpiggy.displaywallet")
        self.settings = [
            {"title": "Wallet Type", "key": "wallet_type", "value_label": None},
            {"title": "LNBits URL", "key": "lnbits_url", "value_label": None},
            {"title": "LNBits Read/Invoice Key", "key": "lnbits_readkey", "value_label": None},
            {"title": "NWC URL", "key": "nwc_url", "value_label": None},
        ]
        self.keyboard = None  # Global reference for keyboard
        self.textarea = None  # Global reference for textarea
        self.msgbox = None    # Global reference for msgbox
        self.create_ui()

    def create_ui(self):
        print("creating ui...")
        self.set_size(lv.pct(100), lv.pct(100))
        self.set_style_pad_all(10, 0)
        self.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        self.set_style_border_width(0, 0)
        
        # Create settings entries
        for setting in self.settings:
            # Container for each setting
            setting_cont = lv.obj(self)
            setting_cont.set_width(lv.pct(100))
            setting_cont.set_height(lv.SIZE_CONTENT)
            setting_cont.set_style_border_width(1, 0)
            setting_cont.set_style_border_color(lv.color_hex(0xCCCCCC), 0)
            setting_cont.set_style_border_side(lv.BORDER_SIDE.BOTTOM, 0)
            setting_cont.set_style_pad_all(8, 0)
            setting_cont.add_flag(lv.obj.FLAG.CLICKABLE)

            # Title label (bold, larger)
            title = lv.label(setting_cont)
            title.set_text(setting["title"])
            title.set_style_text_font(lv.font_montserrat_16, 0)
            title.set_style_text_color(lv.color_hex(0x000000), 0)
            title.set_style_text_decor(lv.TEXT_DECOR.NONE, 0)
            title.set_pos(0, 0)

            # Value label (smaller, below title)
            value = lv.label(setting_cont)
            value.set_text(self.prefs.get_string(setting["key"], "Not set"))
            value.set_style_text_font(lv.font_montserrat_12, 0)
            value.set_style_text_color(lv.color_hex(0x666666), 0)
            value.set_pos(0, 20)
            setting["value_label"] = value  # Store reference for updating

            # Add click event to open msgbox
            setting_cont.add_event_cb(
                lambda e, s=setting: self.open_edit_popup(s), lv.EVENT.CLICKED, None
            )

        # Initialize keyboard (hidden initially)
        self.keyboard = lv.keyboard(lv.screen_active())
        self.keyboard.set_size(lv.pct(100), lv.pct(40))
        self.keyboard.align(lv.ALIGN.BOTTOM_MID, 0, 0)
        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)
        


    def open_edit_popup(self, setting):
        # Close existing msgbox and keyboard if open
        if self.msgbox:
            self.msgbox.delete()
            self.msgbox = None
        if self.keyboard:
            self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)

        # Create msgbox
        self.msgbox = lv.msgbox(self)
        self.msgbox.add_title(setting["title"])
        self.msgbox.set_width(lv.pct(80))
        self.msgbox.center()

        # Create content container
        content = self.msgbox.get_content()
        content.set_style_pad_all(10, 0)
        content.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        # Textarea for editing
        self.textarea = lv.textarea(content)
        self.textarea.set_width(lv.pct(100))
        self.textarea.set_height(lv.SIZE_CONTENT)
        self.textarea.set_text(self.prefs.get_string(setting["key"], ""))
        self.textarea.add_event_cb(self.textarea_cb, lv.EVENT.FOCUSED, None)
        self.textarea.add_event_cb(self.textarea_cb, lv.EVENT.DEFOCUSED, None)

        # Button container
        btn_cont = lv.obj(content)
        btn_cont.set_width(lv.pct(100))
        btn_cont.set_height(lv.SIZE_CONTENT)
        btn_cont.set_style_pad_all(5, 0)
        btn_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn_cont.set_style_flex_main_place(lv.FLEX_ALIGN.SPACE_BETWEEN, 0)

        # Save button
        save_btn = lv.button(btn_cont)
        save_btn.set_size(lv.pct(45), lv.SIZE_CONTENT)
        save_label = lv.label(save_btn)
        save_label.set_text("Save")
        save_label.center()
        save_btn.add_event_cb(
            lambda e, s=setting: self.save_setting(s), lv.EVENT.CLICKED, None
        )

        # Cancel button
        cancel_btn = lv.button(btn_cont)
        cancel_btn.set_size(lv.pct(45), lv.SIZE_CONTENT)
        cancel_label = lv.label(cancel_btn)
        cancel_label.set_text("Cancel")
        cancel_label.center()
        cancel_btn.add_event_cb(self.close_popup, lv.EVENT.CLICKED, None)

    def textarea_cb(self, event):
        code = event.get_code()
        if code == lv.EVENT.FOCUSED:
            self.keyboard.remove_flag(lv.obj.FLAG.HIDDEN)
            self.keyboard.set_textarea(self.textarea)
        elif code == lv.EVENT.DEFOCUSED:
            self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)

    def save_setting(self, setting):
        if self.textarea:
            new_value = self.textarea.get_text()
            editor = self.prefs.edit()
            editor.put_string(setting["key"], new_value)
            editor.commit()
            setting["value_label"].set_text(new_value if new_value else "Not set")
        self.close_popup(None)

    def close_popup(self, event):
        if self.msgbox:
            self.msgbox.delete()
            self.msgbox = None
        if self.keyboard:
            self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)



def settings_button_tap(event):
    global settings_screen
    if not settings_screen:
        settings_screen = SettingsScreen()
    lv.screen_load(settings_screen)

def build_main_ui():
    appscreen.clean()
    balance_label = lv.label(appscreen)
    balance_label.align(lv.ALIGN.TOP_LEFT, 0, 0)
    balance_label.set_style_text_font(lv.font_montserrat_20, 0)
    balance_label.set_text('123456')
    style_line = lv.style_t()
    style_line.init()
    style_line.set_line_width(4)
    style_line.set_line_color(lv.palette_main(lv.PALETTE.PINK))
    style_line.set_line_rounded(True)
    balance_line = lv.line(appscreen)
    balance_line.set_points([{'x':0,'y':35},{'x':300,'y':35}],2)
    balance_line.add_style(style_line, 0)
    settings_button = lv.button(appscreen)
    settings_button.align(lv.ALIGN.BOTTOM_RIGHT, 0, 0)
    snap_label = lv.label(settings_button)
    snap_label.set_text(lv.SYMBOL.SETTINGS)
    snap_label.center()
    settings_button.add_event_cb(settings_button_tap,lv.EVENT.CLICKED,None)


def janitor_cb(timer):
    if lv.screen_active() != appscreen and lv.screen_active() != settings_screen:
        print("app backgrounded, cleaning up...")
        janitor.delete()
        # No cleanups to do, but in a real app, you might stop timers, deinitialize hardware devices you used, close network connections, etc.

janitor = lv.timer_create(janitor_cb, 1000, None)

build_main_ui()

config = mpos.config.SharedPreferences("com.lightningpiggy.displaywallet")

wallet_type = config.get_string("wallet_type")
if wallet_type == "lnbits":
    try:
        wallet = LNBitsWallet(config.get_string("lnbits_url"), config.get_string("lnbits_readkey"))
    except Exception as e:
        print("Couldn't initialize LNBitsWallet because {e}")
elif wallet_type == "nwc":
    try:
        wallet = NWCWallet(config.get_string("nwc_url"))
    except Exception as e:
        print("Couldn't initialize NWCWallet because {e}")
else:
    print(f"No or unsupported wallet type configured: '{wallet_type}'")


