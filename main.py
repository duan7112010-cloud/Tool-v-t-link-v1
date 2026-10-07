# main.py - giao diện Kivy bọc resolver.py
import threading
import webbrowser

from kivy.app import App
from kivy.clock import Clock
from kivy.core.clipboard import Clipboard
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput

from resolver import resolve

Window.clearcolor = (0.07, 0.07, 0.09, 1)
Window.softinput_mode = "below_target"

BTN_COLOR = (0.18, 0.36, 0.85, 1)
BTN_COLOR_ALT = (0.22, 0.22, 0.27, 1)


def format_result(result):
    """Định dạng kết quả giống bản chạy dòng lệnh."""
    lines = []

    for hop in result.get("history", []):
        lines.append(f'{hop["status"]} -> {hop["url"]}')

    if result.get("success"):
        lines.append("")
        lines.append("Link cuối:")
        lines.append(result["final_url"])
    else:
        lines.append("")
        lines.append("Lỗi:")
        lines.append(str(result.get("error", "Không rõ lỗi")))

    return "\n".join(lines)


class ResolverApp(App):
    title = "Link Resolver"

    def build(self):
        self.final_url = None

        root = BoxLayout(
            orientation="vertical",
            padding=dp(14),
            spacing=dp(10),
        )

        root.add_widget(
            Label(
                text="Giải mã link chuyển hướng",
                font_size=sp(20),
                bold=True,
                size_hint_y=None,
                height=dp(44),
            )
        )

        self.url_input = TextInput(
            hint_text="Dán link vào đây",
            multiline=False,
            write_tab=False,
            font_size=sp(16),
            size_hint_y=None,
            height=dp(48),
            padding=(dp(10), dp(12)),
        )
        self.url_input.bind(on_text_validate=self.on_resolve)
        root.add_widget(self.url_input)

        row1 = BoxLayout(
            size_hint_y=None, height=dp(48), spacing=dp(10)
        )
        paste_btn = Button(
            text="Dán",
            background_normal="",
            background_color=BTN_COLOR_ALT,
        )
        paste_btn.bind(on_release=self.on_paste)
        self.resolve_btn = Button(
            text="Giải mã",
            bold=True,
            background_normal="",
            background_color=BTN_COLOR,
        )
        self.resolve_btn.bind(on_release=self.on_resolve)
        row1.add_widget(paste_btn)
        row1.add_widget(self.resolve_btn)
        root.add_widget(row1)

        # Ô kết quả: chỉ đọc nhưng vẫn chọn/copy được bằng cách giữ lâu
        self.result_box = TextInput(
            text="",
            readonly=True,
            multiline=True,
            font_size=sp(14),
            background_color=(0.11, 0.11, 0.14, 1),
            foreground_color=(0.92, 0.92, 0.95, 1),
            padding=(dp(10), dp(10)),
        )
        root.add_widget(self.result_box)

        row2 = BoxLayout(
            size_hint_y=None, height=dp(48), spacing=dp(10)
        )
        self.copy_btn = Button(
            text="Copy link cuối",
            background_normal="",
            background_color=BTN_COLOR_ALT,
            disabled=True,
        )
        self.copy_btn.bind(on_release=self.on_copy)
        self.open_btn = Button(
            text="Mở link",
            background_normal="",
            background_color=BTN_COLOR_ALT,
            disabled=True,
        )
        self.open_btn.bind(on_release=self.on_open)
        row2.add_widget(self.copy_btn)
        row2.add_widget(self.open_btn)
        root.add_widget(row2)

        return root

    # ---- thao tác ----
    def on_paste(self, *_):
        try:
            text = Clipboard.paste() or ""
        except Exception:
            text = ""
        self.url_input.text = text.strip()

    def on_resolve(self, *_):
        url = self.url_input.text.strip()

        if not url:
            self.result_box.text = "Hãy dán link vào ô phía trên."
            return

        self.final_url = None
        self.copy_btn.disabled = True
        self.open_btn.disabled = True
        self.resolve_btn.disabled = True
        self.result_box.text = "Đang giải mã..."

        # Gọi mạng ở luồng riêng để app không bị đơ
        threading.Thread(
            target=self._worker, args=(url,), daemon=True
        ).start()

    def _worker(self, url):
        try:
            result = resolve(url)
        except Exception as e:
            result = {"success": False, "error": str(e), "history": []}

        Clock.schedule_once(lambda dt: self._show(result))

    def _show(self, result):
        self.result_box.text = format_result(result)
        self.resolve_btn.disabled = False

        if result.get("success"):
            self.final_url = result["final_url"]
            self.copy_btn.disabled = False
            self.open_btn.disabled = False

    def on_copy(self, *_):
        if self.final_url:
            Clipboard.copy(self.final_url)
            self.copy_btn.text = "Đã copy!"
            Clock.schedule_once(
                lambda dt: setattr(self.copy_btn, "text", "Copy link cuối"),
                1.5,
            )

    def on_open(self, *_):
        if self.final_url:
            try:
                webbrowser.open(self.final_url)
            except Exception as e:
                self.result_box.text += f"\n\nKhông mở được: {e}"


if __name__ == "__main__":
    ResolverApp().run()
