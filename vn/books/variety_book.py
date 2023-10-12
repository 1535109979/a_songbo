import re
from dataclasses import dataclass, field

from a_songbo.vn.util.sys_exception import common_exception


@dataclass
class Option:
    future: str = None
    option: str = None
    strike_price: int = None


@dataclass
class VarietyBook:
    future: str
    long_options: list
    short_options: list

    future_price: float = None
    long_virtual_2: Option = Option()
    short_virtual_2: Option = Option()

    @classmethod
    def create_by_data(cls, future, options):
        long_option_list = []
        short_option_list = []
        for option in options:
            future = re.match(r'[a-z]+\d+', option).group()
            strike_price = int(re.search(r'\d+$', option).group())

            if re.search(r'[A-Z]', option).group() == 'C':
                long_option_list.append(Option(future=future, option=option, strike_price=strike_price))
            if re.search(r'[A-Z]', option).group() == 'P':
                short_option_list.append(Option(future=future, option=option, strike_price=strike_price))

        return cls(future=future, long_options=long_option_list, short_options=short_option_list)

    @common_exception()
    def update_by_future_price(self, future_price):
        self.long_options.sort(key=lambda x: x.strike_price)
        self.short_options.sort(key=lambda x: x.strike_price)
        self.future_price = future_price

        for i, op in enumerate(self.long_options):
            if op.strike_price > future_price:
                try:
                    self.long_virtual_2 = self.long_options[i+1]
                    break
                except:
                    pass
        for i, op in enumerate(self.short_options):
            if op.strike_price >= future_price:
                try:
                    self.short_virtual_2 = self.short_options[i-2]
                    break
                except:
                    pass


