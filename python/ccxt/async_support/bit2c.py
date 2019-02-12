# -*- coding: utf-8 -*-

# PLEASE DO NOT EDIT THIS FILE, IT IS GENERATED AND WILL BE OVERWRITTEN:
# https://github.com/ccxt/ccxt/blob/master/CONTRIBUTING.md#how-to-contribute-code

from ccxt.async_support.base.exchange import Exchange

# -----------------------------------------------------------------------------

try:
    basestring  # Python 3
except NameError:
    basestring = str  # Python 2
import hashlib
from ccxt.base.errors import ExchangeError
from ccxt.base.errors import ArgumentsRequired


class bit2c (Exchange):

    def describe(self):
        return self.deep_extend(super(bit2c, self).describe(), {
            'id': 'bit2c',
            'name': 'Bit2C',
            'countries': ['IL'],  # Israel
            'rateLimit': 3000,
            'has': {
                'CORS': False,
                'fetchOpenOrders': True,
                'fetchMyTrades': True,
            },
            'urls': {
                'logo': 'https://user-images.githubusercontent.com/1294454/27766119-3593220e-5ece-11e7-8b3a-5a041f6bcc3f.jpg',
                'api': 'https://bit2c.co.il',
                'www': 'https://www.bit2c.co.il',
                'doc': [
                    'https://www.bit2c.co.il/home/api',
                    'https://github.com/OferE/bit2c',
                ],
            },
            'api': {
                'public': {
                    'get': [
                        'Exchanges/{pair}/Ticker',
                        'Exchanges/{pair}/orderbook',
                        'Exchanges/{pair}/trades',
                        'Exchanges/{pair}/lasttrades',
                    ],
                },
                'private': {
                    'post': [
                        'Merchant/CreateCheckout',
                        'Order/AddCoinFundsRequest',
                        'Order/AddFund',
                        'Order/AddOrder',
                        'Order/AddOrderMarketPriceBuy',
                        'Order/AddOrderMarketPriceSell',
                        'Order/CancelOrder',
                        'Order/AddCoinFundsRequest',
                        'Order/AddStopOrder',
                        'Payment/GetMyId',
                        'Payment/Send',
                        'Payment/Pay',
                    ],
                    'get': [
                        'Account/Balance',
                        'Account/Balance/v2',
                        'Order/MyOrders',
                        'Order/GetById',
                        'Order/AccountHistory',
                        'Order/OrderHistory',
                    ],
                },
            },
            'markets': {
                'BTC/NIS': {'id': 'BtcNis', 'symbol': 'BTC/NIS', 'base': 'BTC', 'quote': 'NIS'},
                'ETH/NIS': {'id': 'EthNis', 'symbol': 'ETH/NIS', 'base': 'ETH', 'quote': 'NIS'},
                'BCH/NIS': {'id': 'BchAbcNis', 'symbol': 'BCH/NIS', 'base': 'BCH', 'quote': 'NIS'},
                'LTC/NIS': {'id': 'LtcNis', 'symbol': 'LTC/NIS', 'base': 'LTC', 'quote': 'NIS'},
                'ETC/NIS': {'id': 'EtcNis', 'symbol': 'ETC/NIS', 'base': 'ETC', 'quote': 'NIS'},
                'BTG/NIS': {'id': 'BtgNis', 'symbol': 'BTG/NIS', 'base': 'BTG', 'quote': 'NIS'},
                'BSV/NIS': {'id': 'BchSvNis', 'symbol': 'BSV/NIS', 'base': 'BSV', 'quote': 'NIS'},
            },
            'fees': {
                'trading': {
                    'maker': 0.5 / 100,
                    'taker': 0.5 / 100,
                },
            },
            'options': {
                'fetchTradesMethod': 'public_get_exchanges_pair_lasttrades',
            },
        })

    async def fetch_balance(self, params={}):
        balance = await self.privateGetAccountBalanceV2()
        result = {'info': balance}
        currencies = list(self.currencies.keys())
        for i in range(0, len(currencies)):
            currency = currencies[i]
            account = self.account()
            if currency in balance:
                available = 'AVAILABLE_' + currency
                account['free'] = balance[available]
                account['total'] = balance[currency]
                account['used'] = account['total'] - account['free']
            result[currency] = account
        return self.parse_balance(result)

    async def fetch_order_book(self, symbol, limit=None, params={}):
        orderbook = await self.publicGetExchangesPairOrderbook(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        return self.parse_order_book(orderbook)

    async def fetch_ticker(self, symbol, params={}):
        ticker = await self.publicGetExchangesPairTicker(self.extend({
            'pair': self.market_id(symbol),
        }, params))
        timestamp = self.milliseconds()
        averagePrice = self.safe_float(ticker, 'av')
        baseVolume = self.safe_float(ticker, 'a')
        quoteVolume = None
        if baseVolume is not None and averagePrice is not None:
            quoteVolume = baseVolume * averagePrice
        last = self.safe_float(ticker, 'll')
        return {
            'symbol': symbol,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'high': None,
            'low': None,
            'bid': self.safe_float(ticker, 'h'),
            'bidVolume': None,
            'ask': self.safe_float(ticker, 'l'),
            'askVolume': None,
            'vwap': None,
            'open': None,
            'close': last,
            'last': last,
            'previousClose': None,
            'change': None,
            'percentage': None,
            'average': averagePrice,
            'baseVolume': baseVolume,
            'quoteVolume': quoteVolume,
            'info': ticker,
        }

    async def fetch_trades(self, symbol, since=None, limit=None, params={}):
        market = self.market(symbol)
        method = self.options['fetchTradesMethod']
        response = await getattr(self, method)(self.extend({
            'pair': market['id'],
        }, params))
        if isinstance(response, basestring):
            raise ExchangeError(response)
        return self.parse_trades(response, market, since, limit)

    async def create_order(self, symbol, type, side, amount, price=None, params={}):
        method = 'privatePostOrderAddOrder'
        order = {
            'Amount': amount,
            'Pair': self.market_id(symbol),
        }
        if type == 'market':
            method += 'MarketPrice' + self.capitalize(side)
        else:
            order['Price'] = price
            order['Total'] = amount * price
            order['IsBid'] = (side == 'buy')
        result = await getattr(self, method)(self.extend(order, params))
        return {
            'info': result,
            'id': result['NewOrder']['id'],
        }

    async def cancel_order(self, id, symbol=None, params={}):
        return await self.privatePostOrderCancelOrder({'id': id})

    def sign(self, path, api='public', method='GET', params={}, headers=None, body=None):
        url = self.urls['api'] + '/' + self.implode_params(path, params)
        if api == 'public':
            # lasttrades is the only endpoint that doesn't require the .json extension/suffix
            if path.find('lasttrades') < 0:
                url += '.json'
        else:
            self.check_required_credentials()
            nonce = self.nonce()
            query = self.extend({'nonce': nonce}, params)
            body = self.urlencode(query)
            signature = self.hmac(self.encode(body), self.encode(self.secret), hashlib.sha512, 'base64')
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'key': self.apiKey,
                'sign': self.decode(signature),
            }
        return {'url': url, 'method': method, 'body': body, 'headers': headers}

    async def fetch_open_orders(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        if symbol is None:
            raise ArgumentsRequired(self.id + ' fetchOpenOrders() requires a symbol argument')
        market = self.market(symbol)
        response = await self.privateGetOrderMyOrders(self.extend({
            'pair': market['id'],
        }, params))
        orders = self.safe_value(response, market['id'], {})
        asks = self.safe_value(orders, 'ask')
        bids = self.safe_value(orders, 'bid')
        return self.parse_orders(self.array_concat(asks, bids), market, since, limit)

    def parse_order(self, order, market=None):
        timestamp = order['created']
        price = order['price']
        amount = order['amount']
        cost = price * amount
        symbol = None
        if market is not None:
            symbol = market['symbol']
        side = self.safe_value(order, 'type')
        if side == 0:
            side = 'buy'
        elif side == 1:
            side = 'sell'
        id = self.safe_string(order, 'id')
        status = self.safe_string(order, 'status')
        return {
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'lastTradeTimestamp': None,
            'status': status,
            'symbol': symbol,
            'type': None,
            'side': side,
            'price': price,
            'amount': amount,
            'filled': None,
            'remaining': None,
            'cost': cost,
            'trades': None,
            'fee': None,
            'info': order,
        }

    async def fetch_my_trades(self, symbol=None, since=None, limit=None, params={}):
        await self.load_markets()
        market = None
        method = 'privateGetOrderOrderhistory'
        request = {}
        if limit is not None:
            request['take'] = limit
        request['take'] = limit
        if since is not None:
            request['toTime'] = self.ymd(self.milliseconds(), '.')
            request['fromTime'] = self.ymd(since, '.')
        if symbol is not None:
            market = self.market(symbol)
            request['pair'] = market['id']
        response = await getattr(self, method)(self.extend(request, params))
        return self.parse_trades(response, market, since, limit)

    def parse_trade(self, trade, market=None):
        timestamp = None
        id = None
        price = None
        amount = None
        orderId = None
        feeCost = None
        side = None
        reference = self.safe_string(trade, 'reference')
        if reference is not None:
            timestamp = self.safe_integer(trade, 'ticks') * 1000
            price = self.safe_float(trade, 'price')
            amount = self.safe_float(trade, 'firstAmount')
            reference_parts = reference.split('|')  # reference contains: 'pair|orderId|tradeId'
            if market is None:
                marketId = self.safe_string(trade, 'pair')
                if marketId in self.markets_by_id[marketId]:
                    market = self.markets_by_id[marketId]
                elif reference_parts[0] in self.markets_by_id:
                    market = self.markets_by_id[reference_parts[0]]
            orderId = reference_parts[1]
            id = reference_parts[2]
            side = self.safe_integer(trade, 'action')
            if side == 0:
                side = 'buy'
            elif side == 1:
                side = 'sell'
            feeCost = self.safe_float(trade, 'feeAmount')
        else:
            timestamp = self.safe_integer(trade, 'date') * 1000
            id = self.safe_string(trade, 'tid')
            price = self.safe_float(trade, 'price')
            amount = self.safe_float(trade, 'amount')
            side = self.safe_value(trade, 'isBid')
            if side is not None:
                if side:
                    side = 'buy'
                else:
                    side = 'sell'
        symbol = None
        if market is not None:
            symbol = market['symbol']
        return {
            'info': trade,
            'id': id,
            'timestamp': timestamp,
            'datetime': self.iso8601(timestamp),
            'symbol': symbol,
            'order': orderId,
            'type': None,
            'side': side,
            'takerOrMaker': None,
            'price': price,
            'amount': amount,
            'cost': price * amount,
            'fee': {
                'cost': feeCost,
                'currency': 'NIS',
                'rate': None,
            },
        }
