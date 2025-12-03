"""Weather Application using Flet v0.28.3 with Dynamic Weather Themes and Alerts"""

import flet as ft
from weather_service import WeatherService
from config import Config
import json
from pathlib import Path
from weather_service import WeatherServiceError
import asyncio
from datetime import datetime
import speech_recognition as sr
import pyttsx3
import threading
import pythoncom


class WeatherAlert:
    """Weather alert system for extreme conditions."""
    
    ALERT_TYPES = {
        'extreme_heat': {
            'icon': '🌡️',
            'color': ft.Colors.RED_900,
            'bg_color': ft.Colors.RED_50,
            'title': 'EXTREME HEAT WARNING',
            'severity': 'high'
        },
        'extreme_cold': {
            'icon': '🥶',
            'color': ft.Colors.BLUE_900,
            'bg_color': ft.Colors.BLUE_50,
            'title': 'EXTREME COLD WARNING',
            'severity': 'high'
        },
        'high_wind': {
            'icon': '💨',
            'color': ft.Colors.ORANGE_900,
            'bg_color': ft.Colors.ORANGE_50,
            'title': 'HIGH WIND ADVISORY',
            'severity': 'medium'
        },
        'storm': {
            'icon': '⛈️',
            'color': ft.Colors.PURPLE_900,
            'bg_color': ft.Colors.PURPLE_50,
            'title': 'SEVERE STORM WARNING',
            'severity': 'high'
        },
        'heavy_rain': {
            'icon': '🌧️',
            'color': ft.Colors.INDIGO_900,
            'bg_color': ft.Colors.INDIGO_50,
            'title': 'HEAVY RAIN ALERT',
            'severity': 'medium'
        },
        'snow': {
            'icon': '❄️',
            'color': ft.Colors.LIGHT_BLUE_900,
            'bg_color': ft.Colors.LIGHT_BLUE_50,
            'title': 'SNOW ADVISORY',
            'severity': 'medium'
        },
        'high_humidity': {
            'icon': '💧',
            'color': ft.Colors.TEAL_900,
            'bg_color': ft.Colors.TEAL_50,
            'title': 'HIGH HUMIDITY ALERT',
            'severity': 'low'
        },
        'poor_visibility': {
            'icon': '🌫️',
            'color': ft.Colors.GREY_800,
            'bg_color': ft.Colors.GREY_100,
            'title': 'POOR VISIBILITY WARNING',
            'severity': 'medium'
        }
    }
    
    @staticmethod
    def analyze_weather(weather_data: dict, use_celsius: bool = True) -> list:
        """Analyze weather data and return list of alerts."""
        alerts = []
        
        # Extract weather data
        temp = weather_data.get("main", {}).get("temp", 0)
        feels_like = weather_data.get("main", {}).get("feels_like", 0)
        humidity = weather_data.get("main", {}).get("humidity", 0)
        wind_speed = weather_data.get("wind", {}).get("speed", 0)
        weather_main = weather_data.get("weather", [{}])[0].get("main", "").lower()
        description = weather_data.get("weather", [{}])[0].get("description", "").lower()
        visibility = weather_data.get("visibility", 10000) / 1000  # Convert to km
        
        # Convert to Fahrenheit if needed for comparison
        if not use_celsius:
            temp = (temp * 9/5) + 32
            feels_like = (feels_like * 9/5) + 32
        
        # Extreme Heat (35°C / 95°F or higher)
        threshold_heat = 35 if use_celsius else 95
        if temp >= threshold_heat or feels_like >= threshold_heat:
            recommendation = [
                "Stay indoors during peak heat hours",
                "Drink plenty of water",
                "Avoid strenuous outdoor activities",
                "Wear light, breathable clothing",
                "Use sunscreen (SPF 30+)"
            ]
            alerts.append({
                'type': 'extreme_heat',
                'message': f"Temperature is {temp:.0f}°{'C' if use_celsius else 'F'}. Heat index may be dangerous.",
                'recommendations': recommendation
            })
        
        # Extreme Cold (below 0°C / 32°F)
        threshold_cold = 0 if use_celsius else 32
        if temp <= threshold_cold:
            recommendation = [
                "Bundle up in layers",
                "Limit time outdoors",
                "Protect exposed skin",
                "Watch for signs of frostbite",
                "Keep your home heated"
            ]
            alerts.append({
                'type': 'extreme_cold',
                'message': f"Temperature is {temp:.0f}°{'C' if use_celsius else 'F'}. Risk of hypothermia and frostbite.",
                'recommendations': recommendation
            })
        
        # High Wind (>15 m/s or ~34 mph)
        if wind_speed > 15:
            recommendation = [
                "Secure loose objects outdoors",
                "Avoid parking under trees",
                "Drive carefully, especially high-profile vehicles",
                "Stay away from coastlines"
            ]
            alerts.append({
                'type': 'high_wind',
                'message': f"High winds at {wind_speed:.1f} m/s. Potential for damage.",
                'recommendations': recommendation
            })
        
        # Thunderstorm
        if weather_main == 'thunderstorm':
            recommendation = [
                "Stay indoors and away from windows",
                "Unplug electronic devices",
                "Avoid using corded phones",
                "Do not take a bath or shower",
                "Stay out of water and off boats"
            ]
            alerts.append({
                'type': 'storm',
                'message': "Thunderstorm conditions detected. Lightning and severe weather possible.",
                'recommendations': recommendation
            })
        
        # Heavy Rain
        if weather_main == 'rain' and 'heavy' in description:
            recommendation = [
                "Avoid flooded areas",
                "Drive carefully with headlights on",
                "Stay informed about flash flood warnings",
                "Keep emergency supplies handy"
            ]
            alerts.append({
                'type': 'heavy_rain',
                'message': "Heavy rainfall expected. Potential for flooding.",
                'recommendations': recommendation
            })
        
        # Snow
        if weather_main == 'snow':
            recommendation = [
                "Drive slowly and carefully",
                "Keep winter emergency kit in car",
                "Clear walkways to prevent slips",
                "Dress warmly in layers",
                "Check on elderly neighbors"
            ]
            alerts.append({
                'type': 'snow',
                'message': "Snow conditions present. Travel may be hazardous.",
                'recommendations': recommendation
            })
        
        # High Humidity (>80%)
        if humidity > 80:
            recommendation = [
                "Use dehumidifier indoors",
                "Stay in air-conditioned spaces",
                "Drink water regularly",
                "Take cool showers",
                "Avoid heavy exercise outdoors"
            ]
            alerts.append({
                'type': 'high_humidity',
                'message': f"Humidity at {humidity}%. May feel uncomfortable.",
                'recommendations': recommendation
            })
        
        # Poor Visibility (< 1 km)
        if visibility < 1:
            recommendation = [
                "Use fog lights when driving",
                "Reduce speed significantly",
                "Increase following distance",
                "Avoid unnecessary travel",
                "Stay alert for other vehicles"
            ]
            alerts.append({
                'type': 'poor_visibility',
                'message': f"Visibility reduced to {visibility:.1f} km. Drive with caution.",
                'recommendations': recommendation
            })
        
        # General weather recommendations (no alert, just advice)
        general_recommendations = []
        
        if weather_main == 'clear' and 10 <= (temp if use_celsius else (temp - 32) * 5/9) <= 30:
            general_recommendations.append("Perfect weather! Great day for outdoor activities")
            general_recommendations.append("Don't forget sunscreen")
        
        if weather_main == 'rain' and 'heavy' not in description:
            general_recommendations.append("Bring an umbrella")
            general_recommendations.append("Wear waterproof shoes")
        
        if weather_main == 'clouds':
            general_recommendations.append("Comfortable conditions for outdoor activities")
        
        if 20 <= temp <= 28 and use_celsius:
            general_recommendations.append("Pleasant temperature for walking")
        
        # Add general recommendations if no critical alerts
        if not alerts and general_recommendations:
            alerts.append({
                'type': 'general',
                'message': "Current conditions are favorable",
                'recommendations': general_recommendations
            })
        
        return alerts


class WeatherTheme:
    """Weather condition themes with colors and icons."""
    
    THEMES = {
        # Clear/Sunny conditions
        'clear': {
            'bg_color': '#FFD93D',
            'accent_color': '#FF6B35',
            'text_color': '#2C3E50',
            'card_bg': '#FFF9E6',
            'emoji': '☀️',
            'gradient': ['#FFD93D', '#FFB830']
        },
        # Cloudy conditions
        'clouds': {
            'bg_color': '#95A5A6',
            'accent_color': '#7F8C8D',
            'text_color': '#2C3E50',
            'card_bg': '#ECF0F1',
            'emoji': '☁️',
            'gradient': ['#BDC3C7', '#95A5A6']
        },
        # Rainy conditions
        'rain': {
            'bg_color': '#3498DB',
            'accent_color': '#2980B9',
            'text_color': '#ECF0F1',
            'card_bg': '#5DADE2',
            'emoji': '🌧️',
            'gradient': ['#5DADE2', '#3498DB']
        },
        # Drizzle
        'drizzle': {
            'bg_color': '#5DADE2',
            'accent_color': '#3498DB',
            'text_color': '#2C3E50',
            'card_bg': '#AED6F1',
            'emoji': '🌦️',
            'gradient': ['#AED6F1', '#5DADE2']
        },
        # Thunderstorm
        'thunderstorm': {
            'bg_color': '#34495E',
            'accent_color': '#2C3E50',
            'text_color': '#ECF0F1',
            'card_bg': '#5D6D7E',
            'emoji': '⛈️',
            'gradient': ['#5D6D7E', '#34495E']
        },
        # Snow
        'snow': {
            'bg_color': '#E8F8F5',
            'accent_color': '#85C1E2',
            'text_color': '#2C3E50',
            'card_bg': '#FFFFFF',
            'emoji': '❄️',
            'gradient': ['#FFFFFF', '#E8F8F5']
        },
        # Mist/Fog
        'mist': {
            'bg_color': '#D5DBDB',
            'accent_color': '#AEB6BF',
            'text_color': '#2C3E50',
            'card_bg': '#EAEDED',
            'emoji': '🌫️',
            'gradient': ['#EAEDED', '#D5DBDB']
        },
        'fog': {
            'bg_color': '#D5DBDB',
            'accent_color': '#AEB6BF',
            'text_color': '#2C3E50',
            'card_bg': '#EAEDED',
            'emoji': '🌫️',
            'gradient': ['#EAEDED', '#D5DBDB']
        },
        # Haze/Smoke
        'haze': {
            'bg_color': '#F0E68C',
            'accent_color': '#DAA520',
            'text_color': '#2C3E50',
            'card_bg': '#FAFAD2',
            'emoji': '🌥️',
            'gradient': ['#FAFAD2', '#F0E68C']
        },
        'smoke': {
            'bg_color': '#9E9E9E',
            'accent_color': '#757575',
            'text_color': '#FFFFFF',
            'card_bg': '#BDBDBD',
            'emoji': '💨',
            'gradient': ['#BDBDBD', '#9E9E9E']
        },
        # Dust/Sand
        'dust': {
            'bg_color': '#D4A574',
            'accent_color': '#C19A6B',
            'text_color': '#2C3E50',
            'card_bg': '#E8D5C4',
            'emoji': '🌪️',
            'gradient': ['#E8D5C4', '#D4A574']
        },
        'sand': {
            'bg_color': '#EDC9AF',
            'accent_color': '#C19A6B',
            'text_color': '#2C3E50',
            'card_bg': '#F5E6D3',
            'emoji': '🏜️',
            'gradient': ['#F5E6D3', '#EDC9AF']
        },
        # Tornado
        'tornado': {
            'bg_color': '#5D4E37',
            'accent_color': '#3E2723',
            'text_color': '#FFFFFF',
            'card_bg': '#8B7355',
            'emoji': '🌪️',
            'gradient': ['#8B7355', '#5D4E37']
        },
        # Default
        'default': {
            'bg_color': '#3498DB',
            'accent_color': '#2980B9',
            'text_color': '#2C3E50',
            'card_bg': '#ECF0F1',
            'emoji': '🌍',
            'gradient': ['#5DADE2', '#3498DB']
        }
    }
    
    @staticmethod
    def get_theme(weather_condition: str, is_day: bool = True):
        """Get theme based on weather condition."""
        condition = weather_condition.lower()
        
        # Check for specific conditions
        for key in WeatherTheme.THEMES.keys():
            if key in condition:
                theme = WeatherTheme.THEMES[key].copy()
                
                # Adjust for night time (darker colors)
                if not is_day and key in ['clear', 'clouds']:
                    if key == 'clear':
                        theme['bg_color'] = '#2C3E50'
                        theme['accent_color'] = '#34495E'
                        theme['text_color'] = '#ECF0F1'
                        theme['card_bg'] = '#34495E'
                        theme['emoji'] = '🌙'
                        theme['gradient'] = ['#34495E', '#2C3E50']
                    elif key == 'clouds':
                        theme['bg_color'] = '#5D6D7E'
                        theme['text_color'] = '#ECF0F1'
                        theme['card_bg'] = '#7B8A9B'
                        theme['gradient'] = ['#7B8A9B', '#5D6D7E']
                
                return theme
        
        return WeatherTheme.THEMES['default']


class WeatherApp:
    """Main Weather Application class with dynamic themes and alerts."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.preferences_file = Path("user_preferences.json")
        self.search_history = self.load_history()
        self.preferences = self.load_preferences()
        self.use_celsius = self.preferences.get("use_celsius", True)
        self.current_weather_data = None
        self.current_theme = WeatherTheme.THEMES['default']
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 4000
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8
        self.is_listening = False
        
        # TTS queue
        self.tts_queue = asyncio.Queue()
        self.tts_worker_started = False
        
        self.setup_page()
        self.build_ui()

    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Window properties
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()


    def apply_theme(self, theme: dict, animate: bool = True):
        """Apply weather theme to the page (respects light/dark mode)."""
        self.current_theme = theme
        
        # Only update weather container background, not the main page background
        # Update weather container with themed color
        if hasattr(self, 'weather_container'):
            if animate:
                self.weather_container.bgcolor = theme['card_bg']
                self.weather_container.animate = ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT)
            else:
                self.weather_container.bgcolor = theme['card_bg']
        
        self.page.update()


    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )

        # Theme toggle button
        self.theme_button = ft.IconButton(
            icon=ft.Icons.DARK_MODE,
            tooltip="Toggle theme",
            on_click=self.toggle_theme,
        )

        # Temperature unit toggle
        self.temp_toggle = ft.Switch(
            value=self.use_celsius,
            active_color=ft.Colors.BLUE_700,
            on_change=self.toggle_temperature_unit,
            tooltip="Toggle °C/°F",
        )
        
        self.temp_unit_container = ft.Row(
            [
                ft.Text("°F", size=14, color=ft.Colors.GREY_600),
                self.temp_toggle,
                ft.Text("°C", size=14, color=ft.Colors.GREY_600),
            ],
            spacing=5,
        )

        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.BLUE_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
            expand=True,
        )
        
        # Voice input button
        self.voice_button = ft.IconButton(
            icon=ft.Icons.MIC,
            tooltip="Voice search",
            icon_color=ft.Colors.BLUE_700,
            on_click=self.start_voice_input,
            style=ft.ButtonStyle(
                bgcolor=ft.Colors.BLUE_50,
            ),
        )
        
        # Voice status indicator
        self.voice_status = ft.Text(
            "",
            size=12,
            color=ft.Colors.BLUE_700,
            visible=False,
            italic=True,
        )
        
        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE_700,
            ),
        )
        
        # Search input row
        search_input_row = ft.Row(
            [
                self.city_input,
                self.voice_button,
            ],
            spacing=10,
        )
        
        # Search history section
        self.history_expanded = False
        self.expand_icon = ft.IconButton(
            icon=ft.Icons.EXPAND_MORE,
            tooltip="Show history",
            icon_size=20,
            icon_color=self.current_theme['text_color'],
            on_click=self.toggle_history,
        )
        
        self.history_header = ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.HISTORY, size=20, color=ft.Colors.BLUE_700),
                    ft.Text(
                        "Recent Searches",
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_700,
                    ),
                    ft.Row(
                        [
                            ft.IconButton(
                                icon=ft.Icons.DELETE_OUTLINE,
                                tooltip="Clear history",
                                icon_size=20,
                                on_click=self.clear_history,
                            ),
                            self.expand_icon,
                        ],
                        spacing=0,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=15,
            margin=ft.margin.only(top=10),
            on_click=self.toggle_history,
            ink=True,
        )
        
        # History items list
        self.history_list = ft.Column(spacing=5)
        
        self.history_dropdown = ft.Container(
            content=ft.Column(
                [
                    ft.Container(
                        content=ft.Column(
                            [self.history_list],
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=10,
                        padding=15,
                    ),
                ],
            ),
            visible=False,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            height=0,
        )
        
        # Alert container (initially hidden)
        self.alert_container = ft.Column(
            spacing=10,
            visible=False,
        )
        
        # Weather display container
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=self.current_theme['card_bg'],
            border_radius=10,
            padding=20,
            animate=ft.Animation(800, ft.AnimationCurve.EASE_IN_OUT),
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Title row
        title_row = ft.Row(
            [
                self.title,
                ft.Row(
                    [
                        self.temp_unit_container,
                        self.theme_button,
                    ],
                    spacing=10,
                ),
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        )

        # Main container with standard background
        self.main_container = ft.Container(
            content=ft.Column(
                [
                    title_row,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    search_input_row,
                    self.voice_status,
                    self.search_button,
                    self.history_header,
                    self.history_dropdown,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.alert_container,  # Alerts appear above weather
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            padding=20,
            expand=True,
        )
        
        self.page.add(self.main_container)
        
        # Update history display
        self.update_history_display()


    def create_alert_card(self, alert: dict) -> ft.Container:
        """Create a visual alert card."""
        alert_type = alert.get('type', 'general')
        
        # Skip general recommendations for alert cards
        if alert_type == 'general':
            return None
        
        alert_info = WeatherAlert.ALERT_TYPES.get(alert_type, {})
        
        icon = alert_info.get('icon', '⚠️')
        title = alert_info.get('title', 'WEATHER ADVISORY')
        color = alert_info.get('color', ft.Colors.ORANGE_900)
        bg_color = alert_info.get('bg_color', ft.Colors.ORANGE_50)
        severity = alert_info.get('severity', 'medium')
        
        message = alert.get('message', '')
        recommendations = alert.get('recommendations', [])
        
        # Severity indicator
        severity_colors = {
            'high': ft.Colors.RED_700,
            'medium': ft.Colors.ORANGE_700,
            'low': ft.Colors.YELLOW_700
        }
        severity_color = severity_colors.get(severity, ft.Colors.ORANGE_700)
        
        # Build recommendations list
        rec_widgets = []
        for rec in recommendations[:5]:  # Limit to 5 recommendations
            rec_widgets.append(
                ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.CHECK_CIRCLE,
                            size=16,
                            color=severity_color,
                        ),
                        ft.Text(
                            rec,
                            size=13,
                            color=color,
                        ),
                    ],
                    spacing=8,
                )
            )
        
        alert_card = ft.Container(
            content=ft.Column(
                [
                    # Header with icon and title
                    ft.Row(
                        [
                            ft.Text(
                                icon,
                                size=32,
                            ),
                            ft.Column(
                                [
                                    ft.Row(
                                        [
                                            ft.Text(
                                                title,
                                                size=16,
                                                weight=ft.FontWeight.BOLD,
                                                color=color,
                                            ),
                                            ft.Container(
                                                content=ft.Text(
                                                    severity.upper(),
                                                    size=10,
                                                    weight=ft.FontWeight.BOLD,
                                                    color=ft.Colors.WHITE,
                                                ),
                                                bgcolor=severity_color,
                                                padding=ft.padding.symmetric(horizontal=8, vertical=2),
                                                border_radius=10,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    ft.Text(
                                        message,
                                        size=14,
                                        color=color,
                                        weight=ft.FontWeight.W_500,
                                    ),
                                ],
                                spacing=5,
                                expand=True,
                            ),
                        ],
                        spacing=15,
                    ),
                    
                    # Divider
                    ft.Divider(height=1, color=color) if rec_widgets else ft.Container(),
                    
                    # Recommendations
                    ft.Column(
                        [
                            ft.Text(
                                "Recommendations:",
                                size=13,
                                weight=ft.FontWeight.BOLD,
                                color=color,
                            ),
                            ft.Column(
                                rec_widgets,
                                spacing=5,
                            ),
                        ],
                        spacing=8,
                    ) if rec_widgets else ft.Container(),
                ],
                spacing=12,
            ),
            bgcolor=bg_color,
            border_radius=12,
            padding=20,
            border=ft.border.all(2, severity_color),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=8,
                color=ft.Colors.with_opacity(0.2, color),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(400, ft.AnimationCurve.EASE_OUT),
        )
        
        return alert_card


    def display_alerts(self, alerts: list):
        """Display weather alerts."""
        self.alert_container.controls.clear()
        
        if not alerts:
            self.alert_container.visible = False
            return
        
        # Create alert cards
        for alert in alerts:
            alert_card = self.create_alert_card(alert)
            if alert_card:
                self.alert_container.controls.append(alert_card)
        
        # Show general recommendations if present
        general_alert = next((a for a in alerts if a.get('type') == 'general'), None)
        if general_alert and general_alert.get('recommendations'):
            rec_chips = []
            for rec in general_alert['recommendations']:
                rec_chips.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Icon(ft.Icons.LIGHTBULB_OUTLINE, size=16, color=ft.Colors.BLUE_700),
                                ft.Text(rec, size=13, color=ft.Colors.BLUE_900),
                            ],
                            spacing=8,
                        ),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=20,
                        padding=ft.padding.symmetric(horizontal=15, vertical=8),
                        border=ft.border.all(1, ft.Colors.BLUE_200),
                    )
                )
            
            if rec_chips:
                self.alert_container.controls.append(
                    ft.Container(
                        content=ft.Column(
                            [
                                ft.Text(
                                    "💡 Weather Tips",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE_800,
                                ),
                                ft.Row(
                                    rec_chips,
                                    wrap=True,
                                    spacing=10,
                                    run_spacing=10,
                                ),
                            ],
                            spacing=10,
                        ),
                        bgcolor=ft.Colors.BLUE_50,
                        border_radius=12,
                        padding=15,
                        margin=ft.margin.only(top=5),
                    )
                )
        
        self.alert_container.visible = len(self.alert_container.controls) > 0
        self.page.update()


    def speak(self, text):
        """Convert text to speech."""
        if not self.tts_worker_started:
            self.tts_worker_started = True
            self.page.run_task(self.tts_worker)
        
        asyncio.create_task(self.tts_queue.put(text))
    
    
    async def tts_worker(self):
        """Worker that processes TTS requests."""
        while True:
            try:
                text = await self.tts_queue.get()
                await asyncio.to_thread(self._speak_sync, text)
                self.tts_queue.task_done()
                await asyncio.sleep(0.3)
            except Exception as e:
                print(f"TTS Worker Error: {e}")
    
    
    def _speak_sync(self, text):
        """Synchronous speech function."""
        try:
            pythoncom.CoInitialize()
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            pythoncom.CoUninitialize()
        except Exception as e:
            print(f"TTS Error: {e}")


    def start_voice_input(self, e):
        """Start voice recognition."""
        if self.is_listening:
            return
        self.page.run_task(self.listen_for_voice)


    async def listen_for_voice(self):
        """Listen for voice input."""
        self.is_listening = True
        
        self.voice_button.icon = ft.Icons.MIC_NONE
        self.voice_button.icon_color = ft.Colors.RED_700
        self.voice_button.disabled = True
        self.voice_status.value = "🎤 Listening... Speak now!"
        self.voice_status.visible = True
        self.page.update()
        
        await asyncio.sleep(0.3)
        self.speak("Please say the city name")
        await asyncio.sleep(1.5)
        
        try:
            try:
                import pyaudio
            except ImportError:
                error_msg = "PyAudio is not installed. Please install it using: pip install pyaudio"
                self.voice_status.value = f"❌ {error_msg}"
                self.voice_status.visible = True
                print(error_msg)
                return
            
            with sr.Microphone() as source:
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                print("Listening for speech...")
                audio = await asyncio.to_thread(
                    self.recognizer.listen,
                    source,
                    timeout=10,
                    phrase_time_limit=10
                )
            
            self.voice_status.value = "🔄 Processing speech to text..."
            self.page.update()
            
            print("Converting speech to text...")
            city_name = await asyncio.to_thread(
                self.recognizer.recognize_google,
                audio
            )
            
            print(f"Recognized city: {city_name}")
            city_name = city_name.title()
            
            self.city_input.value = city_name
            self.voice_status.value = f"✓ Recognized: {city_name}"
            self.page.update()
            
            await asyncio.sleep(0.3)
            self.speak(f"Searching weather for {city_name}")
            await asyncio.sleep(2)
            
            await self.get_weather()
            
        except sr.WaitTimeoutError:
            error_msg = "No speech detected. Please try again."
            self.voice_status.value = f"⏱️ {error_msg}"
            self.voice_status.visible = True
            await asyncio.sleep(0.3)
            self.speak(error_msg)
            print("Timeout: No speech detected")
            
        except sr.UnknownValueError:
            error_msg = "Could not understand. Please speak clearly."
            self.voice_status.value = f"❓ {error_msg}"
            self.voice_status.visible = True
            await asyncio.sleep(0.3)
            self.speak(error_msg)
            print("Error: Speech not understood")
            
        except sr.RequestError as e:
            error_msg = "Speech service error. Check your internet."
            self.voice_status.value = f"❌ {error_msg}"
            self.voice_status.visible = True
            await asyncio.sleep(0.3)
            self.speak(error_msg)
            print(f"Request error: {e}")
            
        except Exception as e:
            error_msg = str(e)
            self.voice_status.value = f"❌ Error: {error_msg}"
            self.voice_status.visible = True
            print(f"Unexpected error: {e}")
        
        finally:
            self.is_listening = False
            self.voice_button.icon = ft.Icons.MIC
            self.voice_button.icon_color = ft.Colors.BLUE_700
            self.voice_button.disabled = False
            self.page.update()
            
            await asyncio.sleep(5)
            self.voice_status.visible = False
            self.page.update()


    def toggle_theme(self, e):
        """Toggle between light and dark theme."""
        if self.page.theme_mode == ft.ThemeMode.LIGHT:
            self.page.theme_mode = ft.ThemeMode.DARK
            self.theme_button.icon = ft.Icons.LIGHT_MODE
        else:
            self.page.theme_mode = ft.ThemeMode.LIGHT
            self.theme_button.icon = ft.Icons.DARK_MODE
        self.page.update()

    
    def toggle_temperature_unit(self, e):
        """Toggle between Celsius and Fahrenheit."""
        self.use_celsius = self.temp_toggle.value
        self.save_preferences()
        
        if self.current_weather_data:
            self.page.run_task(self.display_weather, self.current_weather_data)
    
    
    def celsius_to_fahrenheit(self, celsius):
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32
    
    
    def load_preferences(self):
        """Load user preferences."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    
    def save_preferences(self):
        """Save user preferences."""
        try:
            self.preferences["use_celsius"] = self.use_celsius
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")


    def load_history(self):
        """Load search history."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    
    def save_history(self):
        """Save search history."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.search_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    
    def add_to_history(self, city: str):
        """Add city to history."""
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        
        self.search_history.insert(0, {
            'city': city,
            'timestamp': datetime.now().isoformat()
        })
        
        self.search_history = self.search_history[:10]
        self.save_history()
        self.update_history_display()
    
    
    def toggle_history(self, e):
        """Toggle history dropdown."""
        self.history_expanded = not self.history_expanded
        
        if self.history_expanded:
            self.expand_icon.icon = ft.Icons.EXPAND_LESS
            self.history_dropdown.visible = True
            self.history_dropdown.height = min(300, len(self.search_history) * 70 + 30)
        else:
            self.expand_icon.icon = ft.Icons.EXPAND_MORE
            self.history_dropdown.height = 0
        
        self.page.update()
    
    
    def update_history_display(self):
        """Update history display."""
        self.history_list.controls.clear()
        
        if not self.search_history:
            self.history_header.visible = False
            self.history_dropdown.visible = False
            self.page.update()
            return
        
        self.history_header.visible = True
        
        for item in self.search_history:
            city = item.get('city', '')
            timestamp = item.get('timestamp', '')
            
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%b %d, %I:%M %p")
            except:
                time_str = ""
            
            history_item = ft.Container(
                content=ft.Row(
                    [
                        ft.Icon(
                            ft.Icons.LOCATION_ON,
                            size=16,
                            color=ft.Colors.BLUE_600,
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    city,
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.Colors.BLUE_900,
                                ),
                                ft.Text(
                                    time_str,
                                    size=11,
                                    color=ft.Colors.GREY_600,
                                ) if time_str else ft.Container(),
                            ],
                            spacing=2,
                            expand=True,
                        ),
                        ft.IconButton(
                            icon=ft.Icons.CLOSE,
                            icon_size=16,
                            tooltip="Remove from history",
                            on_click=lambda e, c=city: self.remove_from_history(c),
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                ),
                bgcolor=ft.Colors.WHITE,
                border_radius=8,
                padding=10,
                on_click=lambda e, c=city: self.search_from_history(c),
                ink=True,
            )
            
            self.history_list.controls.append(history_item)
        
        self.page.update()
    
    
    def search_from_history(self, city: str):
        """Search from history."""
        self.city_input.value = city
        self.page.update()
        self.page.run_task(self.get_weather)
    
    
    def remove_from_history(self, city: str):
        """Remove from history."""
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        self.save_history()
        self.update_history_display()
    
    
    def clear_history(self, e):
        """Clear all history."""
        self.search_history = []
        self.save_history()
        self.update_history_display()
    
    
    def on_search(self, e):
        """Handle search."""
        self.page.run_task(self.get_weather)


    async def get_weather(self):
        """Fetch and display weather."""
        city = self.city_input.value.strip()
        
        if not city:
            error_msg = "Please enter a city name"
            self.show_error(error_msg)
            self.speak(error_msg)
            return
        
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.alert_container.visible = False
        self.page.update()
        
        try:
            weather_data = await self.weather_service.get_weather(city)
            self.current_weather_data = weather_data
            
            actual_city_name = weather_data.get("name", city)
            self.add_to_history(actual_city_name)
            
            # Get weather condition and apply theme
            weather_condition = weather_data.get("weather", [{}])[0].get("main", "Clear")
            icon_code = weather_data.get("weather", [{}])[0].get("icon", "01d")
            is_day = 'd' in icon_code
            
            # Get and apply appropriate theme
            theme = WeatherTheme.get_theme(weather_condition, is_day)
            self.apply_theme(theme, animate=True)
            
            # Analyze weather and get alerts
            alerts = WeatherAlert.analyze_weather(weather_data, self.use_celsius)
            
            # Display alerts
            self.display_alerts(alerts)
            
            # Display weather
            await self.display_weather(weather_data)
            
            # Voice feedback with alert info
            temp_celsius = weather_data.get("main", {}).get("temp", 0)
            description = weather_data.get("weather", [{}])[0].get("description", "")
            humidity = weather_data.get("main", {}).get("humidity", 0)
            
            if self.use_celsius:
                temp_str = f"{temp_celsius:.0f} degrees Celsius"
            else:
                temp_f = self.celsius_to_fahrenheit(temp_celsius)
                temp_str = f"{temp_f:.0f} degrees Fahrenheit"
            
            feedback = (
                f"Weather for {actual_city_name}. "
                f"{description}. "
                f"Temperature {temp_str}. "
                f"Humidity {humidity} percent."
            )
            
            # Add alert info to voice feedback
            critical_alerts = [a for a in alerts if a.get('type') != 'general']
            if critical_alerts:
                alert_count = len(critical_alerts)
                feedback += f" Warning: {alert_count} weather alert{'s' if alert_count > 1 else ''} detected. Please check the screen for details."
            
            await asyncio.sleep(0.5)
            self.speak(feedback)
        
        except WeatherServiceError as e:
            error_msg = str(e)
            self.show_error(error_msg)
            await asyncio.sleep(0.3)
            self.speak(error_msg)

        except Exception as e:
            error_msg = "An error occurred while fetching weather data"
            self.show_error(str(e))
            await asyncio.sleep(0.3)
            self.speak(error_msg)
        
        finally:
            self.loading.visible = False
            self.page.update()
    
    
    async def display_weather(self, data: dict):
        """Display weather information with themed styling."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp_celsius = data.get("main", {}).get("temp", 0)
        feels_like_celsius = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        weather_main = data.get("weather", [{}])[0].get("main", "Clear")
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        cloudiness = data.get("clouds", {}).get("all", 0)
        
        # Get weather emoji
        is_day = 'd' in icon_code
        theme = WeatherTheme.get_theme(weather_main, is_day)
        weather_emoji = theme['emoji']
        
        # Convert temperature
        if self.use_celsius:
            temp = temp_celsius
            feels_like = feels_like_celsius
            unit = "°C"
        else:
            temp = self.celsius_to_fahrenheit(temp_celsius)
            feels_like = self.celsius_to_fahrenheit(feels_like_celsius)
            unit = "°F"
        
        # Build weather display with themed colors
        self.weather_container.content = ft.Column(
            [
                # Weather emoji banner
                ft.Container(
                    content=ft.Text(
                        weather_emoji,
                        size=80,
                    ),
                    alignment=ft.alignment.center,
                    padding=10,
                ),
                
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=self.current_theme['text_color'],
                ),
                
                # Weather description with icon
                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(
                            description,
                            size=20,
                            italic=True,
                            color=self.current_theme['text_color'],
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                
                # Temperature
                ft.Text(
                    f"{temp:.1f}{unit}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),
                
                ft.Text(
                    f"Feels like {feels_like:.1f}{unit}",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),
                
                ft.Divider(color=self.current_theme['accent_color']),
                
                # Additional info - First row
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%",
                            ft.Colors.BLUE_400,
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s",
                            ft.Colors.CYAN_400,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
                
                # Additional info - Second row
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.COMPRESS,
                            "Pressure",
                            f"{pressure} hPa",
                            ft.Colors.PURPLE_400,
                        ),
                        self.create_info_card(
                            ft.Icons.CLOUD,
                            "Cloudiness",
                            f"{cloudiness}%",
                            ft.Colors.BLUE_GREY_400,
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
        # Update container background
        self.weather_container.bgcolor = self.current_theme['card_bg']
        
        # Animate container appearance
        self.weather_container.animate_opacity = 300
        self.weather_container.opacity = 0
        self.weather_container.visible = True
        self.page.update()

        # Fade in
        await asyncio.sleep(0.1)
        self.weather_container.opacity = 1
        self.page.update()

        self.error_message.visible = False
    
    
    def create_info_card(self, icon, label, value, icon_color):
        """Create info card with fixed colors and custom icon color."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=icon_color),
                    ft.Text(
                        label, 
                        size=12, 
                        color=ft.Colors.GREY_700,
                        text_align=ft.TextAlign.CENTER,
                    ),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                        text_align=ft.TextAlign.CENTER,
                    ),  
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=10,
                color=ft.Colors.with_opacity(0.1, ft.Colors.BLACK),
                offset=ft.Offset(0, 2),
            ),
            animate=ft.Animation(300, ft.AnimationCurve.EASE_IN_OUT),
        )
    
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.alert_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)