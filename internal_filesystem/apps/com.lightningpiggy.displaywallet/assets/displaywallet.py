import time

import mpos.config
import mpos.ui

from wallet import LNBitsWallet, NWCWallet

# screens:
main_screen = None
settings_screen = None
settings_screen_detail = None
qr_screen = None
qr_scanner_screen = None

# widgets
receive_qr = None
balance_label = None
payments_label = None

# variables
wallet = None
receive_qr_data = None

# Settings screen implementation
class SettingsScreen():
    def __init__(self):
        self.prefs = mpos.config.SharedPreferences("com.lightningpiggy.displaywallet")
        self.settings = [
            {"title": "Wallet Type", "key": "wallet_type", "value_label": None, "cont": None},
            {"title": "LNBits URL", "key": "lnbits_url", "value_label": None, "cont": None},
            {"title": "LNBits Read/Invoice Key", "key": "lnbits_readkey", "value_label": None, "cont": None},
            {"title": "Static receive code", "key": "lnbits_static_receive_code", "value_label": None, "cont": None},
            {"title": "NWC URL", "key": "nwc_url", "value_label": None, "cont": None},
        ]
        self.keyboard = None
        self.textarea = None
        self.radio_container = None
        self.active_radio_index = 0  # Track active radio button index
        self.screen = self.create_ui()
        self.update_setting_visibility()  # Initialize visibility based on saved wallet_type

    def create_ui(self):
        screen = lv.obj()
        print("creating ui...")
        screen.set_size(lv.pct(100), lv.pct(100))
        screen.set_style_pad_all(10, 0)
        screen.set_flex_flow(lv.FLEX_FLOW.COLUMN)
        screen.set_style_border_width(0, 0)
        
        # Create settings entries
        for setting in self.settings:
            # Container for each setting
            setting_cont = lv.obj(screen)
            setting_cont.set_width(lv.pct(100))
            setting_cont.set_height(lv.SIZE_CONTENT)
            setting_cont.set_style_border_width(1, 0)
            setting_cont.set_style_border_side(lv.BORDER_SIDE.BOTTOM, 0)
            setting_cont.set_style_pad_all(8, 0)
            setting_cont.add_flag(lv.obj.FLAG.CLICKABLE)
            setting["cont"] = setting_cont  # Store container reference for visibility control

            # Title label (bold, larger)
            title = lv.label(setting_cont)
            title.set_text(setting["title"])
            title.set_style_text_font(lv.font_montserrat_16, 0)
            title.set_pos(0, 0)

            # Value label (smaller, below title)
            value = lv.label(setting_cont)
            value.set_text(self.prefs.get_string(setting["key"], "Not set"))
            value.set_style_text_font(lv.font_montserrat_12, 0)
            value.set_style_text_color(lv.color_hex(0x666666), 0)
            value.set_pos(0, 20)
            setting["value_label"] = value  # Store reference for updating
            setting_cont.add_event_cb(
                lambda e, s=setting: self.open_edit_popup(s), lv.EVENT.CLICKED, None
            )

        # Initialize keyboard (hidden initially)
        self.keyboard = lv.keyboard(lv.layer_sys())
        self.keyboard.set_size(lv.pct(100), lv.pct(40))
        self.keyboard.align(lv.ALIGN.BOTTOM_MID, 0, 0)
        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)
        self.keyboard.add_event_cb(self.keyboard_cb, lv.EVENT.READY, None)
        self.keyboard.add_event_cb(self.keyboard_cb, lv.EVENT.CANCEL, None)
        return screen

    def hide_keyboard(self, event=None):
        print("hide_keyboard: hiding keyboard")
        self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)

    def show_keyboard(self, event):
        print("showing keyboard")
        self.keyboard.remove_flag(lv.obj.FLAG.HIDDEN)
        self.keyboard.set_textarea(self.textarea)

    def keyboard_cb(self, event=None):
        print("keyboard_cb: Keyboard event triggered")
        code = event.get_code()
        if code == lv.EVENT.READY or code == lv.EVENT.CANCEL:
            print("keyboard_cb: READY or CANCEL or RETURN clicked, hiding keyboard")
            self.hide_keyboard()

    def update_setting_visibility(self):
        wallet_type = self.prefs.get_string("wallet_type", "lnbits")
        for setting in self.settings:
            if setting["key"].startswith("lnbits_"):
                if wallet_type != "lnbits":
                    setting["cont"].add_flag(lv.obj.FLAG.HIDDEN)
                else:
                    setting["cont"].remove_flag(lv.obj.FLAG.HIDDEN)
            elif setting["key"].startswith("nwc_"):
                if wallet_type != "nwc":
                    setting["cont"].add_flag(lv.obj.FLAG.HIDDEN)
                else:
                    setting["cont"].remove_flag(lv.obj.FLAG.HIDDEN)

    def radio_event_handler(self, event):
        old_cb = self.radio_container.get_child(self.active_radio_index)
        old_cb.remove_state(lv.STATE.CHECKED)
        self.active_radio_index = -1
        for childnr in range(self.radio_container.get_child_count()):
            child = self.radio_container.get_child(childnr)
            state = child.get_state()
            print(f"radio_container child's state: {state}")
            if state != lv.STATE.DEFAULT: # State can be something like 19 = lv.STATE.HOVERED & lv.STATE.CHECKED & lv.STATE.FOCUSED
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

    def gotqr_callback(self, success, data):
        print(f"gotqr_callback {success}, {data}")
        if success:
            self.textarea.set_text(data)

    def cambutton_cb(self, event):
        global qr_scanner_screen
        print("cambutton clicked!")
        import captureqr
        qr_scanner_screen = captureqr.scanqr(self.gotqr_callback)
        if qr_scanner_screen:
            mpos.ui.load_screen(qr_scanner_screen)

    def open_edit_popup(self, setting):
        global settings_screen_detail
        # Close existing msgbox and keyboard if open
        if settings_screen_detail:
            try:
                settings_screen_detail.delete()
            except Exception as e:
                print(f"Warning: could not delete settings_screen_detail: {e}")
        if self.keyboard:
            self.keyboard.add_flag(lv.obj.FLAG.HIDDEN)

        # Create msgbox
        settings_screen_detail = lv.obj()
        settings_screen_detail.set_style_pad_all(10, 0)
        settings_screen_detail.set_flex_flow(lv.FLEX_FLOW.COLUMN)

        top_cont = lv.obj(settings_screen_detail)
        top_cont.set_width(lv.pct(100))
        top_cont.set_height(lv.SIZE_CONTENT)
        top_cont.set_style_pad_all(0, 0)
        top_cont.set_flex_flow(lv.FLEX_FLOW.ROW)
        top_cont.set_style_flex_main_place(lv.FLEX_ALIGN.SPACE_BETWEEN, 0)

        setting_label = lv.label(top_cont)
        setting_label.set_text(setting["title"])
        setting_label.align(lv.ALIGN.TOP_LEFT,0,0)
        setting_label.set_style_text_font(lv.font_montserrat_22, 0)

        # Camera for text
        self.cambutton = lv.button(top_cont)
        self.cambutton.align(lv.ALIGN.TOP_RIGHT,0,0)
        self.cambuttonlabel = lv.label(self.cambutton)
        self.cambuttonlabel.set_text("CAM")
        self.cambuttonlabel.center()
        self.cambutton.add_event_cb(self.cambutton_cb, lv.EVENT.CLICKED, None)

        if setting["key"] == "wallet_type":
            # Create container for radio buttons
            self.radio_container = lv.obj(settings_screen_detail)
            self.radio_container.set_width(lv.pct(100))
            self.radio_container.set_height(lv.SIZE_CONTENT)
            self.radio_container.set_flex_flow(lv.FLEX_FLOW.COLUMN)
            self.radio_container.add_event_cb(self.radio_event_handler, lv.EVENT.CLICKED, None)

            # Create radio buttons
            options = [("LNBits", "lnbits"), ("Nostr Wallet Connect", "nwc")]
            current_wallet = self.prefs.get_string("wallet_type", "lnbits")
            self.active_radio_index = 0 if current_wallet == "lnbits" else 1

            for i, (text, _) in enumerate(options):
                cb = self.create_radio_button(self.radio_container, text, i)
                if i == self.active_radio_index:
                    cb.add_state(lv.STATE.CHECKED)
        else:
            # Textarea for other settings
            self.textarea = lv.textarea(settings_screen_detail)
            self.textarea.set_width(lv.pct(100))
            self.textarea.set_height(lv.SIZE_CONTENT)
            self.textarea.set_text(self.prefs.get_string(setting["key"], ""))
            self.textarea.add_event_cb(self.show_keyboard, lv.EVENT.CLICKED, None)
            self.textarea.add_event_cb(self.show_keyboard, lv.EVENT.FOCUSED, None)
            self.textarea.add_event_cb(self.hide_keyboard, lv.EVENT.DEFOCUSED, None)

        # Button container
        btn_cont = lv.obj(settings_screen_detail)
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
        save_btn.add_event_cb(lambda e, s=setting: self.save_setting(s), lv.EVENT.CLICKED, None)

        # Cancel button
        cancel_btn = lv.button(btn_cont)
        cancel_btn.set_size(lv.pct(45), lv.SIZE_CONTENT)
        cancel_label = lv.label(cancel_btn)
        cancel_label.set_text("Cancel")
        cancel_label.center()
        cancel_btn.add_event_cb(self.close_popup, lv.EVENT.CLICKED, None)

        mpos.ui.load_screen(settings_screen_detail)

    def save_setting(self, setting):
        if setting["key"] == "wallet_type" and self.radio_container:
            selected_idx = self.active_radio_index
            new_value = "lnbits" if selected_idx == 0 else "nwc"
        elif self.textarea:
            new_value = self.textarea.get_text()
        else:
            new_value = ""
        editor = self.prefs.edit()
        editor.put_string(setting["key"], new_value)
        editor.commit()
        setting["value_label"].set_text(new_value if new_value else "Not set")
        if setting["key"] == "wallet_type":
            self.update_setting_visibility()
        self.close_popup(None)

    def close_popup(self, event):
        global settings_screen_detail
        mpos.ui.back_screen()
        if settings_screen_detail:
            settings_screen_detail.delete()
        if self.keyboard:
            self.hide_keyboard()


def settings_button_tap(event):
    global settings_screen, wallet
    if not settings_screen:
        settings_screen = SettingsScreen().screen
    wallet.stop()
    mpos.ui.load_screen(settings_screen)

def main_ui_set_defaults():
    global balance_label, payments_label, receive_qr
    balance_label.set_text(lv.SYMBOL.REFRESH)
    payments_label.set_text(lv.SYMBOL.REFRESH)
    receive_qr.update("", len(""))

def qr_clicked_cb(event):
    global qr_screen, big_receive_qr, receive_qr_data
    print("QR clicked")
    qr_screen = lv.obj()
    big_receive_qr = lv.qrcode(qr_screen)
    big_receive_qr.set_size(240) # TODO: make this dynamic
    big_receive_qr.set_dark_color(lv.color_black())
    big_receive_qr.set_light_color(lv.color_white())
    big_receive_qr.center()
    big_receive_qr.set_style_border_color(lv.color_white(), 0)
    big_receive_qr.set_style_border_width(3, 0);
    big_receive_qr.update(receive_qr_data, len(receive_qr_data))
    mpos.ui.load_screen(qr_screen)


def build_main_ui():
    global main_screen, balance_label, payments_label, receive_qr
    main_screen = lv.obj()
    main_screen.set_style_pad_all(10, 0)
    balance_label = lv.label(main_screen)
    balance_label.align(lv.ALIGN.TOP_LEFT, 0, 0)
    balance_label.set_style_text_font(lv.font_montserrat_22, 0)
    receive_qr = lv.qrcode(main_screen)
    receive_qr.set_size(50)
    receive_qr.set_dark_color(lv.color_black())
    receive_qr.set_light_color(lv.color_white())
    receive_qr.align(lv.ALIGN.TOP_RIGHT,0,0)
    receive_qr.set_style_border_color(lv.color_white(), 0)
    receive_qr.set_style_border_width(3, 0);
    receive_qr.add_flag(lv.obj.FLAG.CLICKABLE)
    receive_qr.add_event_cb(qr_clicked_cb,lv.EVENT.CLICKED,None)
    style_line = lv.style_t()
    style_line.init()
    style_line.set_line_width(2)
    style_line.set_line_color(lv.palette_main(lv.PALETTE.PINK))
    style_line.set_line_rounded(True)
    balance_line = lv.line(main_screen)
    balance_line.set_points([{'x':0,'y':35},{'x':200,'y':35}],2)
    balance_line.add_style(style_line, 0)
    payments_label = lv.label(main_screen)
    payments_label.align_to(balance_line,lv.ALIGN.OUT_BOTTOM_LEFT,0,10)
    payments_label.set_style_text_font(lv.font_montserrat_16, 0)
    settings_button = lv.button(main_screen)
    settings_button.align(lv.ALIGN.BOTTOM_RIGHT, 0, 0)
    snap_label = lv.label(settings_button)
    snap_label.set_text(lv.SYMBOL.SETTINGS)
    snap_label.center()
    settings_button.add_event_cb(settings_button_tap,lv.EVENT.CLICKED,None)
    mpos.ui.load_screen(main_screen)


def redraw_balance_cb():
    global balance_label
    balance_label.set_text(str(wallet.last_known_balance))

def redraw_payments_cb():
    global payments_label
    print("redrawing payments")
    payments_label.set_text(str(wallet.payment_list))

def janitor_cb(timer):
    global wallet, config, receive_qr_data
    if lv.screen_active() == main_screen and (not wallet or not wallet.is_running()): # just started the app or just returned from settings_screen
        main_ui_set_defaults()
        config = mpos.config.SharedPreferences("com.lightningpiggy.displaywallet")
        wallet_type = config.get_string("wallet_type")
        if wallet_type == "lnbits":
            try:
                receive_qr_data = config.get_string("lnbits_static_receive_code")
                wallet = LNBitsWallet(config.get_string("lnbits_url"), config.get_string("lnbits_readkey"))
            except Exception as e:
                print(f"Couldn't initialize LNBitsWallet because: {e}")
        elif wallet_type == "nwc":
            try:
                wallet = NWCWallet(config.get_string("nwc_url"))
                receive_qr_data = wallet.lud16
            except Exception as e:
                print(f"Couldn't initialize NWCWallet because: {e}")
        else:
            print(f"No or unsupported wallet type configured: '{wallet_type}'")
        if receive_qr_data:
            print(f"Setting static_receive_code: {receive_qr_data}")
            receive_qr.update(receive_qr_data, len(receive_qr_data))
        if wallet:
            print("Starting wallet...")
            wallet.start(redraw_balance_cb, redraw_payments_cb)
        else:
            print("ERROR: could not start any wallet!") # maybe call the error callback to show the error to the user
    elif lv.screen_active() != main_screen and lv.screen_active() != settings_screen and lv.screen_active() != qr_screen and lv.screen_active() != settings_screen_detail and lv.screen_active() != qr_scanner_screen:
        print("app backgrounded, cleaning up...")
        janitor.delete()
        wallet.stop()
        if settings_screen:
            settings_screen.delete()
        if main_screen:
            main_screen.delete()

build_main_ui()

janitor = lv.timer_create(janitor_cb, 500, None)
