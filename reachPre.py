import os
from glob import glob
import zipfile
import pandas as pd
import shutil
import fiona
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

def process_zip_file(file, output_dir):
    """
    处理单个ZIP文件，解压其中的Shapefile并读取内容，返回DataFrame。
    使用Fiona选择字段以减少内存占用。
    """
    # 定义需要的字段
    fields_to_keep = ['reach_id', 'time', 'wse','width','reach_q_b',
                      'dark_frac','ice_clim_f','obs_frac_n','xovr_cal_q']  # 替换为需保留字段

    try:
        # 解压文件
        with zipfile.ZipFile(file, 'r') as zip_ref:
            basename = os.path.basename(file)
            extract_dir = os.path.join(output_dir, basename[:-4])
            zip_ref.extractall(extract_dir)

        # 读取Shapefile文件路径
        shp_file = os.path.join(extract_dir, f"{basename[:-4]}.shp")

        # 使用Fiona读取Shapefile，仅保留需要的字段
        records = []
        with fiona.open(shp_file, 'r') as src:
            for feature in src:
                properties =  {key: feature["properties"][key] for key in fields_to_keep}
                

                # 过滤掉不需要的数据
                if properties['time'] > -1 and properties['xovr_cal_q'] is not None:
                    record = {# 将需要的字段添加到记录中
                        "reach_id": properties['reach_id'],
                        "time": properties['time'],
                        "wse": properties['wse'],
                        "width": properties['width'],
                        "reach_q_b": properties['reach_q_b'],
                        "dark_frac": properties['dark_frac'],
                        "ice_clim_f": properties['ice_clim_f'],
                        "obs_frac_n": properties['obs_frac_n'],
                        "xovr_cal_q": properties['xovr_cal_q'],
                    }
                    records.append(record)

        # 删除解压目录
        shutil.rmtree(extract_dir)

        # 如果没有有效记录，返回None
        if not records:
            return None

        # 转换为DataFrame
        df = pd.DataFrame.from_records(records, columns=['reach_id', 'time', 'reach_q_b','dark_frac','ice_clim_f','obs_frac_n','xovr_cal_q'])
        return df

    except Exception as e:
        print(f"Error processing file {file}: {e}")
        return None

# 定义并行处理函数，同一日的所有文件处理成一个CSV文件
def process_date(date, base_dir, output_dir, num_threads=24):
    """
    处理指定日期的所有 ZIP 文件，使用多线程。
    """
    # 找到目录中对应日期的 ZIP 文件
    reach_files = glob(f'{base_dir}/SWOT_L2_HR_RiverSP_Reach_*_{date}*.zip')
    if len(reach_files) == 0:
        print(f"No files found for date {date}")
        return

    print(f"Processing {len(reach_files)} files for date {date}...")

    # 使用多线程处理文件
    dfs = []
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        results = executor.map(process_zip_file, reach_files, [base_dir] * len(reach_files))
        dfs = [gdf for gdf in results if gdf is not None]

    # 合并所有GeoDataFrame
    if dfs:
        df = pd.concat(dfs, ignore_index=True)  # 合并所有DataFrame
        # 保存为CSV文件
        df.to_csv(f'{output_dir}/reach_{date}.csv', index=False)
        print(f"Finished processing date {date}, saved to {output_dir}/reach_{date}.csv")

        # 打印当前时间（估计计算时间用，可选）
        current_time = datetime.now()
        print(f"当前时间是：{current_time.time()}")
    else:
        print(f"No valid data for date {date}")


base_dir = 'D:/SWOT/RiverSP_V2'         # 输入文件夹路径（SWOT RiverSP原始数据）
output_dir = 'D:/SWOT/RiverSP_s/cycle1-aux3'  # 输出文件夹路径（逐日reach数据）
dates=pd.date_range(start='2023-07-26',end='2024-07-22')
date_strings=dates.strftime("%Y%m%d").tolist()

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

# 遍历日期并处理文件
for date in date_strings:
    process_date(date, base_dir, output_dir, num_threads=24)  # 使用 24 个线程进行并行处理