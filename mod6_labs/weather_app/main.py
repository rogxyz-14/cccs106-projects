"""Weather Application using Flet v0.28.3 with Search History and Voice Input"""

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
import pythoncom  # For Windows COM initialization


class WeatherApp:
    """Main Weather Application class."""
    
    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()
        self.history_file = Path("search_history.json")
        self.preferences_file = Path("user_preferences.json")
        self.search_history = self.load_history()
        self.preferences = self.load_preferences()
        self.use_celsius = self.preferences.get("use_celsius", True)
        self.current_weather_data = None
        
        # Initialize speech recognition with optimized settings
        self.recognizer = sr.Recognizer()
        # Adjust recognition sensitivity for better accuracy
        self.recognizer.energy_threshold = 4000  # Minimum audio energy to consider for recording
        self.recognizer.dynamic_energy_threshold = True  # Automatically adjust to ambient noise
        self.recognizer.pause_threshold = 0.8  # Seconds of non-speaking audio before phrase is considered complete
        self.is_listening = False
        
        # Queue for TTS requests to prevent overlap
        self.tts_queue = asyncio.Queue()
        self.tts_worker_started = False
        
        self.setup_page()
        self.build_ui()

    
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        
        # Custom theme Colors
        self.page.theme = ft.Theme(
            color_scheme_seed=ft.Colors.BLUE,
        )
        
        self.page.padding = 0
        self.page.scroll = ft.ScrollMode.AUTO
        
        # Window properties
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False
        self.page.window.center()


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
        self.temp_unit_text = ft.Text(
            "°C",
            size=16,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.BLUE_700,
        )
        
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
        
        # Search input row (text field + voice button)
        search_input_row = ft.Row(
            [
                self.city_input,
                self.voice_button,
            ],
            spacing=10,
        )
        
        # Search history section with expandable dropdown
        self.history_expanded = False
        self.expand_icon = ft.IconButton(
            icon=ft.Icons.EXPAND_MORE,
            tooltip="Show history",
            icon_size=20,
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
        
        # History items list in a scrollable container
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
        
        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.BLUE_50,
            border_radius=10,
            padding=20,
        )
        
        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )
        
        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)
        
        # Title row with theme toggle button
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

        # Add all components to page with padding container
        self.page.add(
            ft.Container(
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
                        self.weather_container,
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10,
                ),
                padding=20,
                expand=True,
            )
        )
        
        # Update history display
        self.update_history_display()


    def speak(self, text):
        """Convert text to speech using a queue system to prevent overlaps."""
        # Add text to the queue
        if not self.tts_worker_started:
            self.tts_worker_started = True
            self.page.run_task(self.tts_worker)
        
        # Add to queue asynchronously
        asyncio.create_task(self.tts_queue.put(text))
    
    
    async def tts_worker(self):
        """Worker that processes TTS requests one at a time."""
        while True:
            try:
                # Get next text from queue
                text = await self.tts_queue.get()
                
                # Speak the text in a thread
                await asyncio.to_thread(self._speak_sync, text)
                
                # Mark task as done
                self.tts_queue.task_done()
                
                # Small delay between speeches
                await asyncio.sleep(0.3)
                
            except Exception as e:
                print(f"TTS Worker Error: {e}")
    
    
    def _speak_sync(self, text):
        """Synchronous speech function for threading."""
        try:
            # Initialize COM for Windows (required for pyttsx3 on Windows)
            pythoncom.CoInitialize()
            
            # Create a new engine instance for each speech request
            engine = pyttsx3.init()
            
            # Optional: Configure voice properties
            voices = engine.getProperty('voices')
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 0.9)  # Volume (0.0 to 1.0)
            
            engine.say(text)
            engine.runAndWait()
            engine.stop()
            
            # Uninitialize COM
            pythoncom.CoUninitialize()
            
        except Exception as e:
            print(f"TTS Error: {e}")


    def start_voice_input(self, e):
        """Start voice recognition."""
        if self.is_listening:
            return
        
        self.page.run_task(self.listen_for_voice)


    async def listen_for_voice(self):
        """Listen for voice input and convert to text for search."""
        self.is_listening = True
        
        # Update UI to show listening state
        self.voice_button.icon = ft.Icons.MIC_NONE
        self.voice_button.icon_color = ft.Colors.RED_700
        self.voice_button.disabled = True
        self.voice_status.value = "🎤 Listening... Speak now!"
        self.voice_status.visible = True
        self.page.update()
        
        # Wait a moment before speaking instruction
        await asyncio.sleep(0.3)
        
        # Speak instruction to user
        self.speak("Please say the city name")
        
        # Wait for TTS to start
        await asyncio.sleep(1.5)
        
        try:
            # Check if PyAudio is available
            try:
                import pyaudio
            except ImportError:
                error_msg = "PyAudio is not installed. Please install it using: pip install pyaudio"
                self.voice_status.value = f"❌ {error_msg}"
                self.voice_status.visible = True
                print(error_msg)
                print("\nAlternative installation methods:")
                print("1. pip install pyaudio")
                print("2. conda install pyaudio (if using Anaconda)")
                print("3. Download wheel from: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio")
                return
            
            # Use microphone for voice input
            with sr.Microphone() as source:
                # Adjust for ambient noise to improve recognition accuracy
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                
                # Listen for audio input from user
                print("Listening for speech...")
                audio = await asyncio.to_thread(
                    self.recognizer.listen,
                    source,
                    timeout=10,  # Wait up to 10 seconds for speech to start
                    phrase_time_limit=10  # Allow up to 10 seconds of speech
                )
            
            # Update UI to show processing state
            self.voice_status.value = "🔄 Processing speech to text..."
            self.page.update()
            
            # Convert speech to text using Google Speech Recognition
            print("Converting speech to text...")
            city_name = await asyncio.to_thread(
                self.recognizer.recognize_google,
                audio
            )
            
            print(f"Recognized city: {city_name}")
            
            # Capitalize city name properly
            city_name = city_name.title()
            
            # Set the recognized city name in the input field
            self.city_input.value = city_name
            self.voice_status.value = f"✓ Recognized: {city_name}"
            self.page.update()
            
            # Wait before providing confirmation
            await asyncio.sleep(0.3)
            
            # Provide voice feedback to confirm recognition
            self.speak(f"Searching weather for {city_name}")
            
            # Wait for user to see the result and hear confirmation
            await asyncio.sleep(2)
            
            # Automatically trigger weather search
            await self.get_weather()
            
        except sr.WaitTimeoutError:
            # No speech detected within timeout
            error_msg = "No speech detected. Please try again."
            self.voice_status.value = f"⏱️ {error_msg}"
            self.voice_status.visible = True
            await asyncio.sleep(0.3)
            self.speak(error_msg)
            print("Timeout: No speech detected")
            
        except sr.UnknownValueError:
            # Speech was detected but couldn't be understood
            error_msg = "Could not understand. Please speak clearly."
            self.voice_status.value = f"❓ {error_msg}"
            self.voice_status.visible = True
            await asyncio.sleep(0.3)
            self.speak(error_msg)
            print("Error: Speech not understood")
            
        except sr.RequestError as e:
            # API request error (usually internet connection issue)
            error_msg = "Speech service error. Check your internet."
            self.voice_status.value = f"❌ {error_msg}"
            self.voice_status.visible = True
            await asyncio.sleep(0.3)
            self.speak(error_msg)
            print(f"Request error: {e}")
            
        except Exception as e:
            # General error handling
            error_msg = str(e)
            self.voice_status.value = f"❌ Error: {error_msg}"
            self.voice_status.visible = True
            print(f"Unexpected error: {e}")
            
            # Check if it's PyAudio related
            if "PyAudio" in error_msg or "pyaudio" in error_msg.lower():
                print("\nPyAudio installation required!")
                print("Install using: pip install pyaudio")
        
        finally:
            # Reset button state to normal
            self.is_listening = False
            self.voice_button.icon = ft.Icons.MIC
            self.voice_button.icon_color = ft.Colors.BLUE_700
            self.voice_button.disabled = False
            self.page.update()
            
            # Hide status message after 5 seconds
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
        
        # Update display if we have current weather data
        if self.current_weather_data:
            self.page.run_task(self.display_weather, self.current_weather_data)
    
    
    def celsius_to_fahrenheit(self, celsius):
        """Convert Celsius to Fahrenheit."""
        return (celsius * 9/5) + 32
    
    
    def load_preferences(self):
        """Load user preferences from file."""
        if self.preferences_file.exists():
            try:
                with open(self.preferences_file, 'r') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    
    def save_preferences(self):
        """Save user preferences to file."""
        try:
            self.preferences["use_celsius"] = self.use_celsius
            with open(self.preferences_file, 'w') as f:
                json.dump(self.preferences, f, indent=2)
        except Exception as e:
            print(f"Error saving preferences: {e}")


    def load_history(self):
        """Load search history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    
    def save_history(self):
        """Save search history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.search_history, f, indent=2)
        except Exception as e:
            print(f"Error saving history: {e}")
    
    
    def add_to_history(self, city: str):
        """Add city to history."""
        # Remove city if it already exists (to avoid duplicates)
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        
        # Add to beginning of list with timestamp
        self.search_history.insert(0, {
            'city': city,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last 10 searches
        self.search_history = self.search_history[:10]
        
        # Save to file
        self.save_history()
        
        # Update display
        self.update_history_display()
    
    
    def toggle_history(self, e):
        """Toggle history dropdown visibility."""
        self.history_expanded = not self.history_expanded
        
        if self.history_expanded:
            self.expand_icon.icon = ft.Icons.EXPAND_LESS
            self.history_dropdown.visible = True
            self.history_dropdown.height = min(300, len(self.search_history) * 70 + 30)
        else:
            self.expand_icon.icon = ft.Icons.EXPAND_MORE
            self.history_dropdown.height = 0
            # Keep visible=True for animation, will hide after animation completes
        
        self.page.update()
    
    
    def update_history_display(self):
        """Update the history display with current history."""
        # Clear existing history items
        self.history_list.controls.clear()
        
        if not self.search_history:
            self.history_header.visible = False
            self.history_dropdown.visible = False
            self.page.update()
            return
        
        # Show history header
        self.history_header.visible = True
        
        # Add history items
        for item in self.search_history:
            city = item.get('city', '')
            timestamp = item.get('timestamp', '')
            
            # Format timestamp
            try:
                dt = datetime.fromisoformat(timestamp)
                time_str = dt.strftime("%b %d, %I:%M %p")
            except:
                time_str = ""
            
            # Create history item button
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
        """Search weather for a city from history."""
        self.city_input.value = city
        self.page.update()
        self.page.run_task(self.get_weather)
    
    
    def remove_from_history(self, city: str):
        """Remove a city from search history."""
        self.search_history = [item for item in self.search_history 
                               if item.get('city', '').lower() != city.lower()]
        self.save_history()
        self.update_history_display()
    
    
    def clear_history(self, e):
        """Clear all search history."""
        self.search_history = []
        self.save_history()
        self.update_history_display()
    
    
    def on_search(self, e):
        """Handle search button click."""
        self.page.run_task(self.get_weather)


    async def get_weather(self):
        """Fetch and display weather data with voice feedback."""
        city = self.city_input.value.strip()
        
        # Validate input
        if not city:
            error_msg = "Please enter a city name"
            self.show_error(error_msg)
            self.speak(error_msg)
            return
        
        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()
        
        try:
            # Fetch weather data from API
            weather_data = await self.weather_service.get_weather(city)
            
            # Store current weather data for unit conversion
            self.current_weather_data = weather_data
            
            # Add to history (use the actual city name from API response)
            actual_city_name = weather_data.get("name", city)
            self.add_to_history(actual_city_name)
            
            # Display weather information
            await self.display_weather(weather_data)
            
            # Prepare voice feedback with weather details
            temp_celsius = weather_data.get("main", {}).get("temp", 0)
            description = weather_data.get("weather", [{}])[0].get("description", "")
            humidity = weather_data.get("main", {}).get("humidity", 0)
            
            # Format temperature based on user preference
            if self.use_celsius:
                temp_str = f"{temp_celsius:.0f} degrees Celsius"
            else:
                temp_f = self.celsius_to_fahrenheit(temp_celsius)
                temp_str = f"{temp_f:.0f} degrees Fahrenheit"
            
            # Create comprehensive voice feedback
            feedback = (
                f"Weather for {actual_city_name}. "
                f"{description}. "
                f"Temperature {temp_str}. "
                f"Humidity {humidity} percent."
            )
            
            # Wait a moment before speaking results
            await asyncio.sleep(0.5)
            
            # Speak the weather results
            self.speak(feedback)
        
        except WeatherServiceError as e:
            # Show user-friendly error message
            error_msg = str(e)
            self.show_error(error_msg)
            # Wait before speaking error
            await asyncio.sleep(0.3)
            # Provide voice feedback for the error
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
        """Display weather information."""
        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp_celsius = data.get("main", {}).get("temp", 0)
        feels_like_celsius = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)
        pressure = data.get("main", {}).get("pressure", 0)
        cloudiness = data.get("clouds", {}).get("all", 0)
        
        # Convert temperature based on user preference
        if self.use_celsius:
            temp = temp_celsius
            feels_like = feels_like_celsius
            unit = "°C"
        else:
            temp = self.celsius_to_fahrenheit(temp_celsius)
            feels_like = self.celsius_to_fahrenheit(feels_like_celsius)
            unit = "°F"
        
        # Build weather display
        self.weather_container.content = ft.Column(
            [
                # Location
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),
                
                # Weather icon and description
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
                
                ft.Divider(),
                
                # Additional info - First row
                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP,
                            "Humidity",
                            f"{humidity}%",
                            ft.Colors.BLUE_400
                        ),
                        self.create_info_card(
                            ft.Icons.AIR,
                            "Wind Speed",
                            f"{wind_speed} m/s",
                            ft.Colors.LIGHT_BLUE_300
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
                            ft.Colors.PURPLE_300
                        ),
                        self.create_info_card(
                            ft.Icons.CLOUD,
                            "Cloudiness",
                            f"{cloudiness}%",
                            ft.Colors.BLUE_GREY_400
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )
        
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
    
    
    def create_info_card(self, icon, label, value, icon_color=ft.Colors.BLUE_700):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=icon_color),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),  
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )
    
    
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


def main(page: ft.Page):
    """Main entry point."""
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)