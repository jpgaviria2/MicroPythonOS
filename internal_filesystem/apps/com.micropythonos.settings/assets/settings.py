from mpos.apps import Activity, Intent
import mpos.config
import mpos.ui

class Hello(Activity):

    def onCreate(self):
        screen = lv.obj()
        label = lv.label(screen)
        label.set_text('Hello World!')
        label.center()
        self.setContentView(screen)


# Used to list and edit all settings:
class SettingsActivity(Activity):
    def __init__(self):
        super().__init__()
        self.prefs = None
        self.settings = [
            {"title": "Light/Dark Theme", "key": "theme_light_dark", "value_label": None, "cont": None},
            {"title": "Theme Color", "key": "theme_primary_color", "value_label": None, "cont": None, "placeholder": "HTML hex color, like: EC048C"},
            #{"title": "Display Brightness", "key": "display_brightness", "value_label": None, "cont": None, "placeholder": "A value from 0 to 100."},
            # Maybe also add font size (but ideally then all fonts should scale up/down)
            #{"title": "Reboot into Bootloader", "key": "boot_mode", "value_label": None, "cont": None}, # special that doesn't get saved
            #{"title": "Timezone", "key": "timezone", "value_label": None, "cont": None, "placeholder": "Example: Europe/Prague"},
        ]

    def onCreate(self):
        screen = lv.obj()
        print("creating SettingsActivity ui...")
        screen.set_style_pad_all(mpos.ui.pct_of_display_width(2), 0)
        screen.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        screen.set_style_border_width(0, 0)
        self.setContentView(screen)

    def onResume(self, screen):
        # reload settings because the SettingsActivity might have changed them - could be optimized to only load if it did:
        self.prefs = mpos.config.SharedPreferences("com.micropythonos.settings")
        #wallet_type = self.prefs.get_string("wallet_type") # unused

        # Create settings entries
        screen.clean()
        for setting in self.settings:
            # Container for each setting
            setting_cont = lv.obj(screen)
            setting_cont.set_width(lv.pct(100))
            setting_cont.set_height(lv.SIZE_CONTENT)
            setting_cont.set_style_border_width(1, 0)
            setting_cont.set_style_border_side(lv.BORDER_SIDE.BOTTOM, 0)
            setting_cont.set_style_pad_all(mpos.ui.pct_of_display_width(2), 0)
            setting_cont.add_flag(lv.obj.FLAG.CLICKABLE)
            setting["cont"] = setting_cont  # Store container reference for visibility control

            # Title label (bold, larger)
            title = lv.label(setting_cont)
            title.set_text(setting["title"])
            title.set_style_text_font(lv.font_montserrat_16, 0)
            title.set_pos(0, 0)

            # Value label (smaller, below title)
            value = lv.label(setting_cont)
            value.set_text(self.prefs.get_string(setting["key"], "(not set)"))
            value.set_style_text_font(lv.font_montserrat_12, 0)
            value.set_style_text_color(lv.color_hex(0x666666), 0)
            value.set_pos(0, 20)
            setting["value_label"] = value  # Store reference for updating
            setting_cont.add_event_cb(
                lambda e, s=setting: self.startSettingActivity(s), lv.EVENT.CLICKED, None
            )

    def startSettingActivity(self, setting):
        intent = Intent(activity_class=SettingActivity)
        intent.putExtra("setting", setting)
        self.startActivity(intent)

# Used to edit one setting:
class SettingActivity(Activity):

    keyboard = None
    textarea = None
    radio_container = None
    active_radio_index = 0  # Track active radio button index

    def __init__(self):
        super().__init__()
        self.prefs = mpos.config.SharedPreferences("com.micropythonos.settings")
        self.setting = None

    def onCreate(self):
        setting = self.getIntent().extras.get("setting")
        settings_screen_detail = lv.obj()
        settings_screen_detail.set_style_pad_all(mpos.ui.pct_of_display_width(2), 0)
        settings_screen_detail.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        top_cont = lv.obj(settings_screen_detail)
        top_cont.set_width(lv.pct(100))
        top_cont.set_style_border_width(0, 0)
        top_cont.set_height(lv.SIZE_CONTENT)
        top_cont.set_style_pad_all(mpos.ui.pct_of_display_width(1), 0)
        top_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        top_cont.set_style_flex_main_place(lv.FLEX_ALIGN.SPACE_BETWEEN, 0)

        setting_label = lv.label(top_cont)
        setting_label.set_text(setting["title"])
        setting_label.align(lv.ALIGN.TOP_LEFT,0,0)
        setting_label.set_style_text_font(lv.font_montserrat_26, 0)

        if setting["key"] == "theme_light_dark" or setting["key"] == "boot_mode":
            # Create container for radio buttons
            self.radio_container = lv.obj(settings_screen_detail)
            self.radio_container.set_width(lv.pct(100))
            self.radio_container.set_height(lv.SIZE_CONTENT)
            self.radio_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
            self.radio_container.add_event_cb(self.radio_event_handler, lv.EVENT.CLICKED, None)

            # Create radio buttons
            if setting["key"] == "boot_mode":
                options = [("Normal", "normal"), ("Bootloader", "bootloader")]
            else:
                options = [("Light", "light"), ("Dark", "dark")]
            current_setting = self.prefs.get_string(setting["key"])
            self.active_radio_index = -1 # none
            if current_setting == options[0][1]:
                self.active_radio_index = 0
            elif current_setting == options[1][1]:
                self.active_radio_index = 1

            for i, (text, _) in enumerate(options):
                cb = self.create_radio_button(self.radio_container, text, i)
                if i == self.active_radio_index:
                    cb.add_state(lv.STATE.CHECKED)
        else:
            # Textarea for other settings
            self.textarea = lv.textarea(settings_screen_detail)
            self.textarea.set_width(lv.pct(100))
            self.textarea.set_height(lv.SIZE_CONTENT)
            self.textarea.align_to(top_cont, lv.ALIGN.OUT_BOTTOM_MID, 0, 0)
            current = self.prefs.get_string(setting["key"])
            if current:
                self.textarea.set_text(current)
            placeholder = setting.get("placeholder")
            if placeholder:
                self.textarea.set_placeholder_text(placeholder)
            self.textarea.add_event_cb(lambda *args: mpos.ui.anim.smooth_show(self.keyboard), lv.EVENT.CLICKED, None) # it might be focused, but keyboard hidden (because ready/cancel clicked)
            self.textarea.add_event_cb(lambda *args: mpos.ui.anim.smooth_hide(self.keyboard), lv.EVENT.DEFOCUSED, None)
            # Initialize keyboard (hidden initially)
            self.keyboard = lv.keyboard(lv.layer_sys())
            self.keyboard.align(lv.ALIGN.BOTTOM_MID, 0, 0)
            self.keyboard.set_style_min_height(150, 0)
            self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)
            self.keyboard.add_event_cb(lambda *args: mpos.ui.anim.smooth_hide(self.keyboard), lv.EVENT.READY, None)
            self.keyboard.add_event_cb(lambda *args: mpos.ui.anim.smooth_hide(self.keyboard), lv.EVENT.CANCEL, None)
            self.keyboard.set_textarea(self.textarea)

        # Button container
        btn_cont = lv.obj(settings_screen_detail)
        btn_cont.set_width(lv.pct(100))
        btn_cont.set_style_border_width(0, 0)
        btn_cont.set_height(lv.SIZE_CONTENT)
        btn_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        btn_cont.set_style_flex_main_place(lv.FLEX_ALIGN.SPACE_BETWEEN, 0)
        # Save button
        save_btn = lv.button(btn_cont)
        save_btn.set_size(lv.pct(45), lv.SIZE_CONTENT)
        save_label = lv.label(save_btn)
        save_label.set_text("Save")
        save_label.center()
        save_btn.add_event_cb(lambda e, s=setting: self.save_setting(s), lv.EVENT.CLICKED, None)
        # Cancel button
        cancel_btn = lv.button(btn_cont)
        cancel_btn.set_size(lv.pct(45), lv.SIZE_CONTENT)
        cancel_label = lv.label(cancel_btn)
        cancel_label.set_text("Cancel")
        cancel_label.center()
        cancel_btn.add_event_cb(lambda e: self.finish(), lv.EVENT.CLICKED, None)

        if False: # No scan QR button for text settings because they're all short right now
            cambutton = lv.button(settings_screen_detail)
            cambutton.align(lv.ALIGN.BOTTOM_MID,0,0)
            cambutton.set_size(lv.pct(100), lv.pct(30))
            cambuttonlabel = lv.label(cambutton)
            cambuttonlabel.set_text("Scan data from QR code")
            cambuttonlabel.set_style_text_font(lv.font_montserrat_18, 0)
            cambuttonlabel.align(lv.ALIGN.TOP_MID, 0, 0)
            cambuttonlabel2 = lv.label(cambutton)
            cambuttonlabel2.set_text("Tip: Create your own QR code,\nusing https://genqrcode.com or another tool.")
            cambuttonlabel2.set_style_text_font(lv.font_montserrat_10, 0)
            cambuttonlabel2.align(lv.ALIGN.BOTTOM_MID, 0, 0)
            cambutton.add_event_cb(self.cambutton_cb, lv.EVENT.CLICKED, None)

        self.setContentView(settings_screen_detail)

    def onStop(self, screen):
        if self.keyboard:
            mpos.ui.anim.smooth_hide(self.keyboard)

    def radio_event_handler(self, event):
        print("radio_event_handler called")
        if self.active_radio_index >= 0:
            print(f"removing old CHECKED state from child {self.active_radio_index}")
            old_cb = self.radio_container.get_child(self.active_radio_index)
            old_cb.remove_state(lv.STATE.CHECKED)
        self.active_radio_index = -1
        for childnr in range(self.radio_container.get_child_count()):
            child = self.radio_container.get_child(childnr)
            state = child.get_state()
            print(f"radio_container child's state: {state}")
            if state & lv.STATE.CHECKED: # State can be something like 19 = lv.STATE.HOVERED  (16) & lv.STATE.FOCUSED (2) & lv.STATE.CHECKED (1)
                self.active_radio_index = childnr
                break
        print(f"active_radio_index is now {self.active_radio_index}")

    def create_radio_button(self, parent, text, index):
        cb = lv.checkbox(parent)
        cb.set_text(text)
        cb.add_flag(lv.obj.FLAG.EVENT_BUBBLE)
        # Add circular style to indicator for radio button appearance
        style_radio = lv.style_t()
        style_radio.init()
        style_radio.set_radius(lv.RADIUS_CIRCLE)
        cb.add_style(style_radio, lv.PART.INDICATOR)
        style_radio_chk = lv.style_t()
        style_radio_chk.init()
        style_radio_chk.set_bg_image_src(None)
        cb.add_style(style_radio_chk, lv.PART.INDICATOR | lv.STATE.CHECKED)
        return cb

    def gotqr_result_callback_unused(self, result):
        print(f"QR capture finished, result: {result}")
        if result.get("result_code"):
            data = result.get("data")
            print(f"Setting textarea data: {data}")
            self.textarea.set_text(data)

    def cambutton_cb_unused(self, event):
        print("cambutton clicked!")
        self.startActivityForResult(Intent(activity_class=CameraApp).putExtra("scanqr_mode", True), self.gotqr_result_callback)

    def save_setting(self, setting):
        if ( setting["key"] =="theme_light_dark" or setting["key"] == "boot_mode" ) and self.radio_container:
            if setting["key"] == "boot_mode":
                options = [("Normal", "normal"), ("Bootloader", "bootloader")]
            else:
                options = [("Light", "light"), ("Dark", "dark")]
            selected_idx = self.active_radio_index
            if selected_idx == 0:
                new_value = options[0][1]
            elif selected_idx == 1:
                new_value = options[1][1]
            else:
                return # nothing to save
        elif self.textarea:
            new_value = self.textarea.get_text()
        else:
            new_value = ""
        editor = self.prefs.edit()
        editor.put_string(setting["key"], new_value)
        editor.commit()
        setting["value_label"].set_text(new_value if new_value else "(not set)")
        self.finish()
