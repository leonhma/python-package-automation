'''lemon_markets, a wrapper for various lemon.markets enpoints'''

__debug_flag__ = False


import time

from datetime import datetime
from multiprocessing import Process, freeze_support
from websocket import create_connection
from urllib3 import PoolManager


http = PoolManager()


def get_accounts(token):
    '''returns the accounts associated with the given token

       takes as arguments:

       token (required): The token to search associated accounts for'''

    r_accountlist = eval(http.request(method='GET',
                                      url='https://api.lemon.markets/rest/v1/accounts/',
                                      headers={'Authorization': f'Token {token}'}))
    accountlist = []
    for i in r_accountlist['results']:
        accountlist.append(Account(i['uuid'], token))
    if __debug_flag__:
        print(f'[{datetime.utcnow()}:DEBUG] Returned {len(accountlist)} accounts')
    return accountlist


class WebSocket():
    '''a wrapper for the websocket server at lemon.markets'''

    def __init__(self, callback=None,
                 timeout=10,
                 frequency_limit=0):
        '''takes as arguments:

           callback (required): Function to call when websocket data is received.
               The callback should have 3 arguments: time (the unix timestamp of the price data), price (the price at {time}) and
               instrument (the isin of the instrument). But please, LEAVE OUT THE PARANTHESES WHEN PASSING YOUR CALLBACK.

           timeout (optional): The timeout after which the websocket will reconnect. Default is 10

           frequency_limit (optional): The maximum frequency at which the callback will be called.
              Set to 0 to disable maximum frequency. Default is 0'''

        assert None not in [callback, frequency_limit, timeout], 'callback must be specified'

        self._last_message_time = 0
        self._frequency_limit = frequency_limit
        self._timeout = timeout
        self._callback = callback
        self._subscribed = []

        if __debug_flag__:
            print(f'[{datetime.utcnow()}:DEBUG] Initialised WebSocket class')

    def __str__(self):

        return f'Websocket connection to api.lemon.markets. Currently subscribed symbols: {self._subscribed}'

    def __repr__(self):

        return f'Websocket connection to api.lemon.markets. Currently subscribed symbols: {self._subscribed}'

    def __del__(self):
        '''do not call this!'''
        try:
            if self._ws_process.is_alive():
                self._ws_process.terminate()
                if __debug_flag__:
                    print(f'[{datetime.utcnow()}:DEBUG] Stopped worker because class reference was deleted')
        except Exception:
            pass

    def _ws_worker(self):
        '''do not call this!'''
        if __debug_flag__:
            print(f'[{datetime.utcnow()}:DEBUG] Opened websocket connection')
        while True:
            ws = create_connection('ws://api.lemon.markets/streams/v1/marketdata', timeout=self._timeout)
            for each in self._subscribed:
                ws.send('{"action": "subscribe", "type": "trades", "specifier": "with-uncovered", "value": "%s"}' % (each))
            while True:
                try:
                    response = eval(ws.recv())
                    if(time.time()-self._last_message_time > self._frequency_limit):
                        self._callback(instrument=response['isin'], price=response['price'], time=response['date'])
                except Exception:
                    break
            ws.close()
            if __debug_flag__:
                print(f'[{datetime.utcnow()}:DEBUG] Reopening websocket connection (caused by timeout ({self._timeout}) or serverside disconnect)')

    def subscribe(self, instrument=None):
        '''subscribe to realtime data from the given instrument

           takes as arguments:

           instrument (required): the isin of the instrument you want to sunscribe to (for Tesla this would be 'US88160R1014')'''

        assert instrument is not None, 'instrument must be specified'
        if instrument in self._subscribed:
            return
        self._subscribed.append(instrument)

        if __debug_flag__:
            debug_str = ''
            debug_str += f'Subscribed to data from {instrument}. Current list of subscribed symbols is {self._subscribed}. '

        if len(self._subscribed) == 1:
            self._ws_process = Process(target=self._ws_worker, name='lemon_websocket')
            self._ws_process.start()
            if __debug_flag__:
                debug_str += f'Started worker'

        if __debug_flag__:
            print(f'[{datetime.utcnow()}:DEBUG] {debug_str}')

    def unsubscribe(self, instrument=None):
        '''unsubscribe from realtime data for the given instrument

           takes as arguments:

           instrument (required): the isin of the instrument you want to unsunscribe from (for Tesla this would be 'US88160R1014')'''

        assert instrument is not None, 'instrument must be specified'

        try:
            self._subscribed.remove(instrument)
        except ValueError:
            pass

        if __debug_flag__:
            debug_str = ''
            debug_str += f'Unsubscribed from data for {instrument}. Current list of subscribed symbols is {self._subscribed}. '

        if len(self._subscribed) == 0:
            self._ws_process.terminate()
            if __debug_flag__:
                debug_str += 'Stopped worker (no websockets active)'

        print(f'[{datetime.utcnow()}:DEBUG] {debug_str}')

    def get_subscribed(self):
        '''returns a list containing all subscribed instruments'''
        return self._subscribed


class Account():
    '''a wrapper for retrieving account data from lemon.markets'''

    def __init__(self, account_uuid=None, token=None):
        '''takes as arguments:

           account_uuid (required): The uuid of the account. You can get all accounts for a token using lemon_markets.get_accounts()

           token (required): the token used to authenticate with lemon.markets. You can get this from your dashboard'''

        assert None not in [account_uuid, token], 'account_uuid and token must be specified. debug_flag cannot be None'

        self._uuid = account_uuid
        self._token = token
        self._auth_header = {'Authorization': f'Token {self._token}'}
        r_userdata = eval(http.request(method='GET',
                                       url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/',
                                       headers={'Authorization': f'Token {self.token}'}))
        self._name = r_userdata['name']
        self._type = r_userdata['type']
        self._currency = r_userdata['currency']

    def __str__(self):

        return f'''account at lemon.markets,
                      uuid: {self._uuid},
                      token: {self._token},
                      name: {self._name},
                      type: {self._type},
                      currency: {self._currency}'''

    def __repr__(self):

        return '''account at lemon.markets,
                      uuid: {self._uuid},
                      token: {self._token},
                      name: {self._name},
                      type: {self._type},
                      currency: {self._currency}'''

    def get_name(self):
        '''returns the name of the account'''
        return self._name

    def get_uuid(self):
        '''returns the UUID of the account'''
        return self._uuid

    def get_token(self):
        '''returns the token associated with the account'''
        return self._token

    def get_type(self):
        '''returns the type of the account'''
        return self._type

    def get_currency(self):
        '''returns the currency of the account'''
        return self._currency

    def create_order(self,
                     side=None,
                     instrument=None,
                     quantity=None,
                     order_type=None,
                     valid_until=time.time()+300,
                     limit_price=None,
                     stop_price=None):

        '''creates an order

           takes as arguments:

           side (required): either 'buy' or 'sell. its quite obvious

           instrument (required): the isin of the instrument you want to create an order for.

           quantity (required): the amount you want to order.

           order_type (required): either 'market', 'stop_market', 'limit' or 'stop_limit'.

           valid_until (optional): the unix timestamp you want the order to be valid until.

           limit_price (required if order_type is 'limit' or 'stop_limit'): the order shoulb be placed at {limit_price} or better

           stop_price (required if order_type is 'stop' or 'stop_limit'): the will be placed at {stop_price}'''

        assert None not in [side, instrument, quantity, valid_until, order_type], \
            'side, instrument and quantity have to be specified. valid_until cannot be None'
        assert order_type in ['limit', 'stop_limit', 'market', 'stop_market'], \
            'Unsupported order type!'
        if limit_price is None and 'limit' in order_type:
            raise AssertionError(f'Limit price has to be specified for orders of type {order_type}')
        if stop_price is None and 'stop' in order_type:
            raise AssertionError(f'Stop price has to be specified for orders of type {order_type}')

        r_order = http.request_encode_body(method='POST',
                                           url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/orders/',
                                           headers=self._auth_header,
                                           fields={
                                               'instrument': instrument,
                                               'side': side,
                                               'quantity': quantity,
                                               'valid_until': valid_until,
                                               'type': order_type,
                                               'limit_price': limit_price,
                                               'stop_price': stop_price
                                           })
        if r_order.status != 200:
            if __debug_flag__:
                print(f'[{datetime.utcnow()}:DEBUG] Creating order failed. Returned status code: {r_order.status}')
            return None

        if __debug_flag__:
            print(f'[{datetime.utcnow()}:DEBUG] Created order (side: {side}, instrument: {instrument}, quantity: {quantity}, ',
                  f'valid_until: {valid_until}), order_type: {order_type}, limit_price: {limit_price}, stop_price: {stop_price}')
        return eval(r_order)['uuid']

    def delete_order(self,
                     order_uuid=None):
        '''deletes the specified order

           takes as arguments:

           order_uuid: the order UUID you get returned from create_order() or list_orders()'''

        assert order_uuid is not None, 'order_uuid must be specified'

        http.request(method='DELETE',
                     url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/orders/{order_uuid}/',
                     headers={
                         'Authorization': f'Token {self._token}'
                     })

        orderlist = eval(self.list_orders(99999, 0))

        for item in orderlist:
            if item['uuid'] == order_uuid:
                return False
                if __debug_flag__:
                    print(f'[{datetime.utcnow()}:DEBUG] Order could not be deleted')
        if __debug_flag__:
            print(f'[{datetime.utcnow()}:DEBUG] Order successfully deleted')
        return True

    def list_orders(self,
                    limit=200,
                    offset=0,
                    side=None,
                    order_type=None,
                    status=None,
                    created_at_until=None,
                    created_at_from=None):
        '''returns a list of all open orders in your account

           takes as arguments:

           limit (optional): the limit of results to return

           offset (optional): how many of the first results to skip

           side (optional): either 'buy' or 'sell' the type of order you want to filter for

           order_type (optional): the type of orders you want to filter for, e.g. 'limit', 'stop_limit', 'market' or 'stop_market'

           status (optional): the status of the orders you want to filter for

           created_at_until (optional): the unix timestamp before which the orders you want to filter for were created

           created_at_from (optional): the unix timestamp after which the orders you want to filter for were created'''

        assert None not in [limit, offset], 'limit and offset cannot be None'

        r_orderlist = eval(http.request_encode_url(method='GET',
                                                   url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/orders/',
                                                   headers=self._auth_header,
                                                   fields={
                                                       'limit': limit,
                                                       'offset': offset,
                                                       'side': side,
                                                       'execution_type': order_type,
                                                       'status': status,
                                                       'created_at_until': created_at_until,
                                                       'created_at_from': created_at_from
                                                   }))
        return r_orderlist['results']

    def order_get_info(self,
                       order_id=None):
        '''returns info about the order

           takes as arguments:

           order_id (required): the order id you want to get information about.
           can be obtained as the return of create_order() or through calling list_orders()'''

        assert order_id is not None, 'order_uuid must be specified'

        r_orderinfo = eval(http.request(method='GET',
                                        url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/orders/{order_id}/',
                                        headers=self._auth_header))
        return r_orderinfo

    def list_transactions(self,
                          limit=200,
                          offset=0,
                          date_from=None,
                          date_until=None):
        '''returns a list of transactions

           takes as arguments:

           limit (optional): the maximum number of results to return

           offset (optional): how many of the first results to skip

           date_from (optional): the date after which the filtered transactions were made

           date_until (optional): the date before which the filtered transactions were made'''

        assert None not in [limit, offset], 'limit and offset cannot be None'

        r_transactlist = eval(http.request_encode_url(method='GET',
                                                      url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/transactions/',
                                                      headers=self._auth_header,
                                                      fields={
                                                          'limit': limit,
                                                          'offset': offset,
                                                          'date_until': date_until,
                                                          'date_from': date_from
                                                      }))
        return r_transactlist

    def transaction_get_info(self,
                             transaction_id=None):
        '''returns info about the transaction

           takes as arguments:

           transaction_id (required): the transaction id you want to get information about.
           can be obtained through calling list_transactions()'''

        assert transaction_id is not None, 'transaction_id must be specified'

        r_transactinfo = eval(http.request(method='GET',
                                           url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/transactions/{transaction_id}/',
                                           headers=self._auth_header))
        return r_transactinfo

    def get_portfolio(self,
                      mode='aggregated',
                      instrument=None,
                      offset=0,
                      limit=200):
        '''get all positions in the portfolio

           takes as arguments:

           mode (optional): the mode in which you want to get the result returned.
           either 'aggregated' (all positions of one instrument are combined), 'seperated' (all orders are listed seperately)
           or 'instrument' (only returns positions for the specified instrument). default is 'aggregated'

           instrument (required if mode is 'instrument'): the isin of the instrument you want to get results for

           offset (optional): how many of the first results to skip. set to 0 if nothing should be skipped. default is 0

           limit (optional): the maximum number of results to return. default is 200'''

        assert None not in [mode, offset, limit], 'mode, offset and limit must not be None'
        assert mode in ['aggregated', 'instrument', 'seperated'], 'Unsupported mode!'

        if mode is 'aggregated' or 'seperated':
            if mode is 'seperated':
                url = f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/portfolio/aggregated'
            else:
                url = f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/portfolio/'
            pages_list = []
            while limit > 0:
                if limit >= 1000:
                    pages_list.append(1000)
                    limit -= 1000
                else:
                    pages_list.append(limit)
                    limit = 0

            portfolio_list = []
            for i, item in enumerate(pages_list):
                page_offset = i*1000+offset
                r_aggregated = eval(http.request_encode_url(method='GET',
                                                            url=url,
                                                            headers=self._auth_header,
                                                            fields={
                                                                'limit': item,
                                                                'offset': page_offset
                                                            }))
                portfolio_list += r_aggregated['results']
                if r_aggregated['next'] == 'null':
                    break
            return portfolio_list

        assert instrument is not None, 'instrument must be specified for mode "instrument"'
        r_portfolio = eval(http.request(method='GET',
                                        url=f'https://api.lemon.markets/rest/v1/accounts/{self._uuid}/portfolio/{instrument}/aggregated/',
                                        headers=self._auth_header))
        return r_portfolio

# todo

    def get_trades_intraday(self,
                            instrument=None,
                            order=None,
                            date_from=None,
                            date_until=None,
                            limit=None,
                            offset=None):
        '''returns a list of the trades of today

           takes as arguments:

           instrument (required): the isin of the instrument to get data date_from

           order (optional): either 'date' or '-date' depends on if you want to get newest or oldest first. default is unordered

           date_from (optional): the unix timestamp after which all trades listed should have happened

           date_to (optional): the unix timestamp before which all trades listed should have happened

           limit (optional): the maximum number of trades to return. default in infinite

           offset (optional): how many of the first results to skip'''

        assert instrument is not None, 'instrument must be specified'
        assert order is None or order in ['date', '-date']

        r_tradeslist = http.request_encode_url(method='GET',
                                               url=f'https://api.lemon.markets/rest/v1/data/instruments/{instrument}/ticks/',
                                               headers=self._auth_header,
                                               fields={
                                                   'ordering': order,
                                                   'date_from': date_from,
                                                   'date_until': date_until,
                                                   'limit': limit,
                                                   'offset': offset
                                               })
        return r_tradeslist

    def get_latest_trade(self,
                         instrument=None):
        '''returns info on the latest trades

           takes as arguments:

           instrument (required): the isin of the instrument you want to get the latest trade from'''

        assert instrument is not None, 'instrument must be specified'

        r_latesttrade = eval(http.request(method='GET',
                                          url=f'https://api.lemon.markets/rest/v1/data/instruments/{instrument}/ticks/latest/',
                                          headers=self._auth_header))
        return r_latesttrade

    def get_m1_candlesticks(self,
                            instrument=None,
                            order=None,
                            date_from=None,
                            date_until=None,
                            limit=1000,
                            offset=0):
        '''returns a list of 1-minute-granularity candles of today

           takes as arguments:

           instrument (required): the isin of the instrument to get data date_from

           order (optional): either 'date' or '-date' depends on if you want to get newest or oldest first. default is unordered

           date_from (optional): the unix timestamp after which all candles listed should have been recorded

           date_to (optional): the unix timestamp before which all candles listed should have been recorded

           limit (optional): the maximum number of candles to return. default in infinite

           offset (optional): how many of the first results to skip'''

        assert None not in [instrument, limit, offset], 'instrument must be specified'

        pages_list = []
        while limit > 0:
            if limit >= 1000:
                pages_list.append(1000)
                limit -= 1000
            else:
                pages_list.append(limit)
                limit = 0

        m1candles_list = []
        for i, item in enumerate(pages_list):
            page_offset = i*1000+offset
            r_m1candles = eval(http.request_encode_url(method='GET',
                                                       url=f'https://api.lemon.markets/rest/v1/data/instruments/{instrument}/candle/m1/',
                                                       headers=self._auth_header,
                                                       fields={
                                                           'ordering': order,
                                                           'date_from': date_from,
                                                           'date_until': date_until,
                                                           'limit': item,
                                                           'offset': page_offset
                                                       }))
            m1candles_list += r_m1candles['results']
            if r_m1candles['next'] == 'null':
                break
        return m1candles_list

    def get_m1_candlesticks_latest(self,
                                   instrument=None):
        '''returns the latest m1-candlestick

           takes as arguments:

           instrument (required): the isin of the instrument you want to get the latest candle from'''

        assert instrument is not None, 'instrument must be specified'

        r_latestcandle = eval(http.request(method='GET',
                                           url=f'https://api.lemon.markets/rest/v1/data/instruments/{instrument}/candle/m1/latest/',
                                           headers=self._auth_header))
        return r_latestcandle


class REST():
    def __str__(self):
        return 'REST object'

    def __repr__(self):
        return 'REST object'

    def list_instruments(self,
                         search=None,
                         instrument_type=None,
                         limit=1000,
                         offset=0):
        '''get a list of all available instruments

           takes as arguments:

           search (optional): search for isin, wkn or title

           instrument_type (optional): either 'stocks', 'bonds' or 'fonds'

           limit (optional): maximum number of instruments to return. default is 1000

           offset (optional): number of first results to skip'''

        assert None not in [limit, offset], 'limit and offset cannot be None'

        page_list = []
        while limit > 0:
            if limit >= 1000:
                page_list.append(1000)
                limit -= 1000
            else:
                page_list.append(limit)
                limit = 0

        instrument_list = []
        for i, item in enumerate(page_list):
            page_offset = i*1000+offset
            r_instrumentlist = eval(http.request_encode_url(method='GET',
                                                            url='https://api.lemon.markets/rest/v1/data/instruments/',
                                                            fields={
                                                                'search': search,
                                                                'type': instrument_type,
                                                                'limit': item,
                                                                'offset': page_offset
                                                            }))
            instrument_list += r_instrumentlist['results']
            if r_instrumentlist['next'] == 'null':
                break
        return instrument_list

    def instrument_get_info(self,
                            instrument=None):
        '''returns info about the given instrument

           takes as arguments:

           instrument (required): the isin of the instrument you want to get info about'''

        assert instrument is not None, 'instrument must be specified'

        r_instrumentinfo = eval(http.request(method='GET',
                                             url=f'https://api.lemon.markets/rest/v1/data/instruments/{instrument}/'))
        return r_instrumentinfo


if __name__ == '__main__':
    time.sleep(10)
    freeze_support()
    if __debug_flag__:
        print(f'[{datetime.utcnow()}:DEBUG] Added freeze_support()')
