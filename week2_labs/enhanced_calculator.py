import flet as ft


class CalculatorApp(ft.Container):
    def __init__(self):
        super().__init__()
        self.result = ft.Text(value="0", color=ft.Colors.WHITE, size=20)
        self.current_input = "0"

        # Build UI
        self.width = 350
        self.bgcolor = ft.Colors.BLACK
        self.border_radius = ft.border_radius.all(20)
        self.padding = 20
        self.content = self._build_content()

    # Base button class
    class CalcButton(ft.ElevatedButton):
        def __init__(self, text, button_clicked, expand=1):
            super().__init__()
            self.text = text
            self.expand = expand
            self.on_click = button_clicked
            self.data = text

    # Specialized buttons
    class DigitButton(CalcButton):
        def __init__(self, text, button_clicked, expand=1):
            CalculatorApp.CalcButton.__init__(self, text, button_clicked, expand)
            self.bgcolor = ft.Colors.WHITE24
            self.color = ft.Colors.WHITE

    class ActionButton(CalcButton):
        def __init__(self, text, button_clicked):
            CalculatorApp.CalcButton.__init__(self, text, button_clicked)
            self.bgcolor = ft.Colors.ORANGE
            self.color = ft.Colors.WHITE

    class ExtraActionButton(CalcButton):
        def __init__(self, text, button_clicked):
            CalculatorApp.CalcButton.__init__(self, text, button_clicked)
            self.bgcolor = ft.Colors.BLUE_GREY_100
            self.color = ft.Colors.BLACK

    # Event handler for buttons
    def button_clicked(self, e):
        btn = e.control.data

        if btn == "AC":
            self.current_input = "0"
        elif btn == "+/-":
            if self.current_input.startswith("-"):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = "-" + self.current_input
        elif btn == "%":
            try:
                self.current_input = str(float(self.current_input) / 100)
            except:
                self.current_input = "Error"
        elif btn == "=":
            try:
                self.current_input = str(eval(self.current_input))
            except:
                self.current_input = "Error"
        else:
            if self.current_input == "0" and btn not in [".", "+", "-", "*", "/"]:
                self.current_input = btn
            else:
                self.current_input += btn

        self.result.value = self.current_input
        self.update()

    # Build calculator UI
    def _build_content(self):
        return ft.Column(
            controls=[
                ft.Row(controls=[self.result], alignment="end"),
                ft.Row(
                    controls=[
                        self.ExtraActionButton("AC", self.button_clicked),
                        self.ExtraActionButton("+/-", self.button_clicked),
                        self.ExtraActionButton("%", self.button_clicked),
                        self.ActionButton("/", self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        self.DigitButton("7", self.button_clicked),
                        self.DigitButton("8", self.button_clicked),
                        self.DigitButton("9", self.button_clicked),
                        self.ActionButton("*", self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        self.DigitButton("4", self.button_clicked),
                        self.DigitButton("5", self.button_clicked),
                        self.DigitButton("6", self.button_clicked),
                        self.ActionButton("-", self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        self.DigitButton("1", self.button_clicked),
                        self.DigitButton("2", self.button_clicked),
                        self.DigitButton("3", self.button_clicked),
                        self.ActionButton("+", self.button_clicked),
                    ]
                ),
                ft.Row(
                    controls=[
                        self.DigitButton("0", self.button_clicked, expand=2),
                        self.DigitButton(".", self.button_clicked),
                        self.ActionButton("=", self.button_clicked),
                    ]
                ),
            ]
        )


def main(page: ft.Page):
    page.title = "Calculator App"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"
    page.add(CalculatorApp())


ft.app(main)
