from itertools import cycle
import logging

from kivy import properties as kproperties
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.audio import SoundLoader
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget

Config.set('graphics', 'width', '300')
Config.set('graphics', 'height', '500')


logger = logging.getLogger('')


# Work, Break, & Long break times in mins
TIME_DEFS = {'W': 25, 'B': 5, 'LB': 15}
SCREEN_REFRESH_FREQ = 1  # Can be used to speed up clock for dev


class Timer(Widget):
    DISPLAY_TIME = kproperties.ObjectProperty(None)
    COUNT_MINS_WORD_SEQUENCE = kproperties.StringProperty('W,B,W,B,W,B,W,B,LB')
    COUNT_TIMES_CYCLER = None

    def setup_pomo(self):
        count_time, time_type, time_seq = self.get_next_wait_time()
        self.set_display_time(
            time_int_to_str(count_time)
        )
        self.IS_OFF = True
        self.set_progress_bar(0, count_time)
        self.dingling_sound = SoundLoader.load('media/dingling.wav')

    def __init__(self, *args, **kwargs):
        super(Timer, self).__init__(*args, **kwargs)
        self.setup_pomo()

    def start_pomo(self):
        Clock.schedule_interval(self.update, SCREEN_REFRESH_FREQ)
        self.IS_OFF = False

    def stop_pomo(self):
        Clock.unschedule(self.update)
        self.setup_pomo()
        self.IS_OFF = True

    def set_display_time(self, time_str):
        self.display_time.text = str(time_str)

    def get_display_time(self):
        return time_str_to_int(self.display_time.text)

    def get_next_wait_time(self):
        """Returns tuple of (remaining time, time def str, count seq)
        """
        if not getattr(self, 'TIMES_CYCLER', None):
            self._cycle_iterations = 0
            self.TIMES_CYCLER = cycle(self.COUNT_MINS_WORD_SEQUENCE.split(','))

        time_type = next(self.TIMES_CYCLER)
        self._time_amt = TIME_DEFS[time_type] * 60
        self._cycle_iterations += 1
        return (self._time_amt, time_type, self._cycle_iterations)

    def update(self, *args, **kwargs):
        remaining_time = self.get_display_time() - 1
        if remaining_time < 0:
            remaining_time, time_type, _ = self.get_next_wait_time()
            if time_type in ['B', 'LB']: self.dingling_sound.play()
        self.set_display_time(time_int_to_str(remaining_time))

        # Advance progress bar
        self.set_progress_bar(self._time_amt -remaining_time, self._time_amt)

    def set_progress_bar(self, value, max):
        self.display_bar.value = value
        self.display_bar.max = max


class Controls(Widget):
    def __init__(self, pomo, *args, **kwargs):
        super(Controls, self).__init__(*args, **kwargs)
        self.pomo = pomo
        self.ding_sound = SoundLoader.load('media/ding.wav')

    def btn_pressed(self):
        self.ding_sound.play()
        if self.pomo.IS_OFF:
            self.pomo.start_pomo()
            self.control_btn.text = 'Reset'
        else:
            self.pomo.stop_pomo()
            self.control_btn.text = 'Start'

def time_str_to_int(time_str):
    """Returns time int from str,
    e.g.: 01:30 --> 90
    """
    hr, min = time_str.split(':')
    return (int(hr) * 60) + int(min)


def time_int_to_str(time_int):
    """Returns time string,
    e.g.: 90 --> 01:30
    """
    hr, min = divmod(time_int, 60)
    return "{:0>2d}:{:0>2d}".format(hr, min)


class PomodoroApp(App):
    def build(self):
        f = FloatLayout()

        t = Timer()
        c = Controls(pomo=t)

        f.add_widget(t)
        f.add_widget(c)

        return f


if __name__ == '__main__':
    PomodoroApp().run()
