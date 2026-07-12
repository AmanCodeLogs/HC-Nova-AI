# pyrefly: ignore [missing-import]
import flet as ft
import requests
import sys

# Detect if running in browser (Pyodide)
IS_PYODIDE = "pyodide" in sys.modules

# Render API URL
BACKEND_URL = "https://hc-nova-ai.onrender.com"

async def main(page: ft.Page):
    page.title = "HealthCurve Nova AI"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0f172a"  # Sleek slate-900 background
    page.padding = 15

    # Configure custom styling parameters
    accent_teal = "#2dd4bf"
    accent_teal_dark = "#115e59"
    accent_teal_deep = "#042f2e"
    card_bg = "#1e293b"
    border_color = "#334155"
    text_primary = "#f8fafc"
    text_secondary = "#94a3b8"

    # UI Components for Tab 1 (Prescription Tracker)
    result_list = ft.ListView(spacing=12, expand=True)
    progress_ring = ft.ProgressRing(width=24, height=24, stroke_width=3, color=accent_teal, visible=False)

    async def on_upload_result(e: ft.FilePickerResultEvent):
        if not e.files:
            return

        progress_ring.visible = True
        result_list.controls.clear()
        page.update()

        try:
            file_info = e.files[0]
            file_name = file_info.name
            file_bytes = file_info.bytes

            # Desktop fallback: read path if bytes are None (local desktop mode)
            if not file_bytes and file_info.path:
                with open(file_info.path, "rb") as f:
                    file_bytes = f.read()

            if not file_bytes:
                raise Exception("Unable to read file content.")

            url = f"{BACKEND_URL}/api/ocr/process"

            if IS_PYODIDE:
                from js import File, FormData
                from pyodide.http import pyfetch
                
                # Create native JS File & FormData for fetch in WebAssembly
                js_file = File.new([file_bytes], file_name, {"type": "application/octet-stream"})
                form_data = FormData.new()
                form_data.append("prescription", js_file)

                response = await pyfetch(url, method="POST", body=form_data)
                if response.status != 200:
                    raise Exception(f"Server returned status {response.status}")
                data = await response.json()
            else:
                # Desktop fallback (synchronous requests library)
                response = requests.post(url, files={"prescription": (file_name, file_bytes)})
                if response.status_code != 200:
                    raise Exception(f"Server returned status {response.status_code}")
                data = response.json()

            timetable = data.get("timetable", [])
            if not timetable:
                result_list.controls.append(
                    ft.Text("No medication schedules extracted. Try a clearer photo.", color=text_secondary, italic=True)
                )
            else:
                for item in timetable:
                    result_list.controls.append(
                        ft.Container(
                            content=ft.Row([
                                ft.Container(
                                    content=ft.Icon(ft.icons.MEDICATION, color=accent_teal, size=28),
                                    bgcolor="#1e293b",
                                    padding=10,
                                    border_radius=8
                                ),
                                ft.Column([
                                    ft.Text(item.get('medicine', 'Unknown Medicine'), size=16, weight=ft.FontWeight.BOLD, color=text_primary),
                                    ft.Row([
                                        ft.Icon(ft.icons.ACCESS_TIME, size=14, color=accent_teal),
                                        ft.Text(f"{item.get('time', 'N/A')}", size=13, color=text_secondary),
                                        ft.Text(" • ", color="#475569"),
                                        ft.Icon(ft.icons.OPACITY, size=14, color=accent_teal),
                                        ft.Text(f"{item.get('dosage', 'N/A')}", size=13, color=text_secondary),
                                    ], spacing=5),
                                    ft.Text(f"Instructions: {item.get('instructions')}", size=12, italic=True, color=text_secondary) if item.get('instructions') else ft.Container()
                                ], expand=True, spacing=2)
                            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                            bgcolor=card_bg,
                            padding=15,
                            border_radius=10,
                            border=ft.border.all(1, border_color),
                        )
                    )
        except Exception as ex:
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Error processing prescription: {str(ex)}", color="#f87171"),
                bgcolor="#7f1d1d"
            )
            page.snack_bar.open = True
        finally:
            progress_ring.visible = False
            page.update()

    file_picker = ft.FilePicker(on_result=on_upload_result)
    page.overlay.append(file_picker)

    # UI Components for Tab 2 (Nova AI Chat)
    chat_history = ft.ListView(expand=True, spacing=10, auto_scroll=True)
    
    # Pre-populate with welcome message
    chat_history.controls.append(
        ft.Row([
            ft.Container(
                content=ft.Column([
                    ft.Text("Nova AI", size=11, color=accent_teal, weight=ft.FontWeight.BOLD),
                    ft.Text("Hello! I am Nova AI, your HealthCurve assistant. Ask me questions about your medications, dosage instructions, or general health concerns.", color=text_primary)
                ], spacing=2),
                bgcolor=card_bg,
                padding=12,
                border_radius=ft.border_radius.only(top_left=12, top_right=12, bottom_right=12),
                border=ft.border.all(1, border_color),
                max_width=450
            )
        ], alignment=ft.MainAxisAlignment.START)
    )

    async def send_chat_message(e):
        user_message = chat_input.value.strip()
        if not user_message:
            return

        chat_input.value = ""
        chat_input.disabled = True
        chat_send_btn.disabled = True

        # Append User Message
        chat_history.controls.append(
            ft.Row([
                ft.Container(
                    content=ft.Column([
                        ft.Text("You", size=11, color="#22d3ee", weight=ft.FontWeight.BOLD),
                        ft.Text(user_message, color=text_primary)
                    ], spacing=2),
                    bgcolor=accent_teal_deep,
                    padding=12,
                    border_radius=ft.border_radius.only(top_left=12, top_right=12, bottom_left=12),
                    border=ft.border.all(1, accent_teal_dark),
                    max_width=450
                )
            ], alignment=ft.MainAxisAlignment.END)
        )

        # Temporary typing indicator
        typing_indicator = ft.Row([
            ft.Container(
                content=ft.Row([
                    ft.ProgressRing(width=14, height=14, stroke_width=2, color=accent_teal),
                    ft.Text("Nova is typing...", size=13, color=text_secondary)
                ], spacing=8),
                bgcolor=card_bg,
                padding=12,
                border_radius=ft.border_radius.only(top_left=12, top_right=12, bottom_right=12),
                border=ft.border.all(1, border_color),
            )
        ], alignment=ft.MainAxisAlignment.START)
        
        chat_history.controls.append(typing_indicator)
        page.update()

        try:
            url = f"{BACKEND_URL}/api/chat"
            payload = {"message": user_message}

            if IS_PYODIDE:
                from pyodide.http import pyfetch
                import json
                
                response = await pyfetch(
                    url,
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    body=json.dumps(payload)
                )
                if response.status != 200:
                    raise Exception(f"Server returned status {response.status}")
                data = await response.json()
            else:
                response = requests.post(url, json=payload)
                if response.status_code != 200:
                    raise Exception(f"Server returned status {response.status_code}")
                data = response.json()

            ai_text = data.get("text", "No response received.")

            chat_history.controls.remove(typing_indicator)
            chat_history.controls.append(
                ft.Row([
                    ft.Container(
                        content=ft.Column([
                            ft.Text("Nova AI", size=11, color=accent_teal, weight=ft.FontWeight.BOLD),
                            ft.Text(ai_text, color=text_primary)
                        ], spacing=2),
                        bgcolor=card_bg,
                        padding=12,
                        border_radius=ft.border_radius.only(top_left=12, top_right=12, bottom_right=12),
                        border=ft.border.all(1, border_color),
                        max_width=450
                    )
                ], alignment=ft.MainAxisAlignment.START)
            )
        except Exception as ex:
            if typing_indicator in chat_history.controls:
                chat_history.controls.remove(typing_indicator)
            
            page.snack_bar = ft.SnackBar(
                content=ft.Text(f"Chat error: {str(ex)}", color="#f87171"),
                bgcolor="#7f1d1d"
            )
            page.snack_bar.open = True
        finally:
            chat_input.disabled = False
            chat_send_btn.disabled = False
            chat_input.focus()
            page.update()

    chat_input = ft.TextField(
        hint_text="Ask Nova AI about your prescriptions or symptoms...",
        expand=True,
        border_color=border_color,
        bgcolor="#111827",
        color=text_primary,
        border_radius=8,
        on_submit=send_chat_message
    )
    chat_send_btn = ft.IconButton(
        icon=ft.icons.SEND_ROUNDED,
        icon_color=accent_teal,
        on_click=send_chat_message
    )

    # Tabs definition
    tracker_tab = ft.Container(
        content=ft.Column([
            ft.Text("Upload a prescription image to digitize and extract a personalized medication timetable.", color=text_secondary, size=14),
            ft.Row([
                ft.ElevatedButton(
                    "Upload Prescription",
                    icon=ft.icons.UPLOAD_FILE,
                    style=ft.ButtonStyle(
                        color="#0f172a",
                        bgcolor=accent_teal,
                        shape=ft.RoundedRectangleBorder(radius=8),
                    ),
                    on_click=lambda _: file_picker.pick_files(with_data=True)
                ),
                progress_ring
            ], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(color=border_color, height=20),
            ft.Text("Extracted Timetable", size=16, weight=ft.FontWeight.BOLD, color=text_primary),
            result_list
        ], spacing=15, expand=True),
        padding=ft.padding.only(top=15)
    )

    chat_tab = ft.Container(
        content=ft.Column([
            chat_history,
            ft.Row([
                chat_input,
                chat_send_btn
            ], alignment=ft.MainAxisAlignment.CENTER, spacing=10)
        ], spacing=15, expand=True),
        padding=ft.padding.only(top=15)
    )

    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=250,
        tabs=[
            ft.Tab(
                text="Prescription Tracker",
                icon=ft.icons.TRACK_CHANGES,
                content=tracker_tab
            ),
            ft.Tab(
                text="Nova AI Chat Assistant",
                icon=ft.icons.CHAT_ROUNDED,
                content=chat_tab
            )
        ],
        expand=True
    )

    # Top Header
    header = ft.Container(
        content=ft.Row([
            ft.Icon(ft.icons.HEALTH_AND_SAFETY, color=accent_teal, size=32),
            ft.Column([
                ft.Text("HealthCurve Nova AI", size=22, weight=ft.FontWeight.BOLD, color=text_primary),
                ft.Text("Next-Gen Intelligent Healthcare Companion", size=12, color=text_secondary)
            ], spacing=2)
        ], alignment=ft.MainAxisAlignment.START),
        padding=ft.padding.only(bottom=15),
        border=ft.border.only(bottom=ft.BorderSide(1, border_color))
    )

    page.add(
        ft.Container(
            content=ft.Column([
                header,
                tabs
            ], expand=True),
            expand=True
        )
    )

# Run as a web app
ft.app(target=main, view=ft.AppView.WEB_BROWSER)