import re
import pandas as pd

def process_wifi_data(wifi_df):

    print("Processing wifi data...")

    wifi_df['timestamp'] = wifi_df['timestamp'].apply(int).apply(str)
    wifi_df['timestamp'] = pd.to_datetime(wifi_df['timestamp'], format='%Y%m%d%H%M%S')

    bins = pd.date_range('2024-02-28 11:20:00', '2024-02-28 16:20:00', freq='30 min')
    wifi_df['binned_timestamp'] = pd.cut(wifi_df['timestamp'], bins=bins)

    pivoted_table = wifi_df.pivot_table(index=['binned_timestamp'], 
                                        columns=['bssid'], 
                                        values=['signal_strength'], 
                                        observed=True, 
                                        fill_value=0, 
                                        aggfunc='mean', 
                                        dropna=False)
    
    tabular = pd.DataFrame(pivoted_table.to_records())
    tabular.dropna(inplace=True)

    return tabular

def process_bt_data(bt_data):

    print(f'Processing bluetooth data...')

    pattern = r'(\d{14}) - .*?Device (\S+)'

    unique_bt_devices = {}
    for line in bt_data:
        matches = re.findall(pattern, line)

        for timestamp, bt_device_id in matches:
            if timestamp not in unique_bt_devices:
                unique_bt_devices[timestamp] = {bt_device_id}
            else:
                unique_bt_devices[timestamp].add(bt_device_id)

    bt_df = pd.DataFrame([(timestamp, len(devices)) for timestamp, devices in unique_bt_devices.items()], 
                              columns=['Timestamp', 'Bt_devices_total'])
    
    return bt_df



