
from matplotlib.ticker import FuncFormatter

weekly = "C:/Users/westl/PycharmProjects/pythonProject/weekly.xlsx"


spx_us = pd.read_excel(weekly, sheet_name=0, parse_dates=True)
spx_eps_us = pd.read_excel(weekly, sheet_name=1, parse_dates=True)
spx_bd_us = pd.read_excel(weekly, sheet_name=2, parse_dates=True)

spx_bd = spx_bd_us[['date']].merge(spx_us, on='date', how='left').set_index('date')
spx_eps_us_bd = spx_bd_us[['date']].merge(spx_eps_us, on='date', how='left').set_index('date')

spx_eps_us_bd.columns = ['Fwd EPS']

data_tbl = spx_bd.reset_index().merge(spx_eps_us_bd.reset_index(), on = 'date', how='left')

data_tbl.columns = ['Date','S&P 500','ISM','ISM_ser','Term Premium','Fwd EPS']

data = data_tbl[['Date','S&P 500','ISM','Term Premium','Fwd EPS']]

quarter_end_dates = pd.date_range(start="1985-01-03", end="2025-01-15", freq=pd.offsets.BQuarterEnd())

data = data[data["Date"].isin(quarter_end_dates)]

# 텀프리미엄 3개월 변화량 계산
data["Term Premium Chg"] = data["Term Premium"].diff(1)

# 텀프리미엄 3개월 변화량 표준화
data["Term Premium Chg Std"] = (
    data["Term Premium Chg"] - data["Term Premium Chg"].mean()
) / data["Term Premium Chg"].std()

# 나머지 데이터 3개월 변화율 계산
data["ISM Chg"] = data["ISM"].diff(1)
data["S&P 500 Chg"] = data["S&P 500"].pct_change(1)
data["Fwd EPS Chg"] = data["Fwd EPS"].pct_change(1)

# 2. 구간 나누기 및 데이터 그룹화 (이전 코드와 동일)

# 구간 설정
ranges = np.arange(-2, 2.5, 0.5)  # 2.25를 2.5로 수정
ranges = np.concatenate(([-np.inf], ranges, [np.inf]))

# 데이터 그룹화 (구간 열 추가)
data["Range"] = pd.cut(data["Term Premium Chg Std"], bins=ranges)

# 3. 구간별 평균 변화율 계산 및 그래프 생성을 위한 함수 정의


# 3. 구간별 평균 변화율 계산 및 그래프 생성을 위한 함수 정의

def calculate_and_plot_avg_chg(data, ranges, criteria_col, label, ax):
    sp500_avg_chg_rates = []
    sp500_chg_when_criteria_up = []
    sp500_chg_when_criteria_down = []

    for i in range(len(ranges) - 1):
        lower_bound = ranges[i]
        upper_bound = ranges[i + 1]

        # -inf, +inf 구간 및 1.5~2.0, 2.0~2.5 구간 필터링
        if i == 0:
            filtered_data = data[data["Term Premium Chg Std"] <= ranges[i + 1]]
        elif i == len(ranges) - 2:
            filtered_data = data[data["Term Premium Chg Std"] > ranges[i]]
        elif lower_bound == 1.5:
            filtered_data = data[
                (data["Term Premium Chg Std"] > lower_bound)
                & (data["Term Premium Chg Std"] <= upper_bound)
                ]
        elif lower_bound == 2.0:
            filtered_data = data[
                (data["Term Premium Chg Std"] > lower_bound)
                & (data["Term Premium Chg Std"] <= upper_bound)
                ]
        else:
            filtered_data = data[
                (data["Term Premium Chg Std"] > lower_bound)
                & (data["Term Premium Chg Std"] <= upper_bound)
                ]

        sp500_avg_chg_rate = filtered_data["S&P 500 Chg"].mean()
        sp500_avg_chg_rates.append(sp500_avg_chg_rate)

        sp500_chg_up = filtered_data.loc[
            filtered_data[criteria_col] > 0, "S&P 500 Chg"
        ].mean()
        sp500_chg_when_criteria_up.append(sp500_chg_up)

        sp500_chg_down = filtered_data.loc[
            filtered_data[criteria_col] <= 0, "S&P 500 Chg"
        ].mean()
        sp500_chg_when_criteria_down.append(sp500_chg_down)

    # Generate bar plot
    bar_width = 0.2
    x = np.arange(len(ranges) - 1)

    ax.bar(
        x - bar_width,
        sp500_avg_chg_rates,
        bar_width,
        label=f"S&P 500 Avg Chg"
    )
    ax.bar(
        x,
        sp500_chg_when_criteria_up,
        bar_width,
        label=f"S&P 500 Avg Chg when {label} Up"
    )
    ax.bar(
        x + bar_width,
        sp500_chg_when_criteria_down,
        bar_width,
        label=f"S&P 500 Avg Chg when {label} Down"
    )

    # x축 레이블 생성: -inf, +inf, 1.5~2.0, 2.0~2.5 구간 추가
    x_labels = []
    for i in range(len(ranges) - 1):
        if i == 0:
            x_labels.append(f"≤{ranges[i + 1]:.2f}")
        elif i == len(ranges) - 2:
            x_labels.append(f">{ranges[i]:.2f}")
        elif ranges[i] == 1.5:
            x_labels.append(f"{ranges[i]:.1f}~{ranges[i + 1]:.1f}")
        elif ranges[i] == 2.0:
            x_labels.append(f"{ranges[i]:.1f}~{ranges[i + 1]:.1f}")
        else:
            x_labels.append(f"{ranges[i]:.2f}~{ranges[i + 1]:.2f}")

    # y축 레이블을 %로 변환하는 함수
    def to_percent(y, position):
        # 100을 곱하여 백분율로 표시하고, 소수점 이하 두 자리까지 표시
        return f"{100 * y:.2f}%"

    # y축 포맷터 생성
    formatter = FuncFormatter(to_percent)
    ax.yaxis.set_major_formatter(formatter)

    # x축, y축, 범례 글자 크기 조정
    ax.tick_params(axis="x", labelsize=25)  # x축 레이블 크기 조정
    ax.tick_params(axis="y", labelsize=25)  # y축 레이블 크기 조정
    ax.legend(fontsize=20)  # 범례 글자 크기 조정

    ax.set_xlabel("Term Premium Change Range (Standardized)", fontsize=20)
    ax.set_ylabel("Average 3-Month Change Rate", fontsize=20)
    ax.set_title(f"Average Change Rate by Term Premium Change Range ({label})", fontsize=16)
    ax.set_xticks(x)
    ax.set_xticklabels(x_labels, rotation=45, ha="right")
    ax.grid(True)


# 4. 그래프 생성 (이전 코드와 동일)

# 그래프 1: ISM 기준
fig, ax1 = plt.subplots(figsize=(14, 7))
calculate_and_plot_avg_chg(data, ranges, "ISM Chg", "ISM", ax1)

# x축 레이블이 잘리지 않도록 여유 공간 확보
fig.subplots_adjust(bottom=0.25)


fig, ax1 = plt.subplots(figsize=(14, 7))
calculate_and_plot_avg_chg(
    data, ranges[ranges >= 0], "ISM Chg", "ISM", ax1
)  # data 대신 data_filtered 사용, ranges 조정
fig.subplots_adjust(bottom=0.25)

plt.tight_layout()
plt.show()


# 그래프 2: Fwd EPS 기준
fig, ax2 = plt.subplots(figsize=(14, 7))
calculate_and_plot_avg_chg(data, ranges, "Fwd EPS Chg", "Fwd EPS", ax2)

# x축 레이블이 잘리지 않도록 여유 공간 확보
fig.subplots_adjust(bottom=0.25)

plt.tight_layout()
plt.show()


filtered_data_special = data[(data["Term Premium Chg Std"] > 0.5) & (data["S&P 500 Chg"] > 0)]

# 텀프리미엄 표준화 점수가 1보다 큰 구간(Range) 확인
term_premium_ranges_greater_than_1 = filtered_data_special[["Date","S&P 500 Chg","ISM Chg"]].unique()

print("텀프리미엄 표준화 점수가 1보다 큰 구간:")
for r in term_premium_ranges_greater_than_1:
    print(r)



# 3. 텀프리미엄 표준화 점수 시계열 그래프 생성
data_2023 = data[data["Date"] >= pd.Timestamp("2023-01-01")]
fig, ax = plt.subplots(figsize=(14, 7))

# 텀프리미엄 표준화 점수 막대 그래프 생성 (2023년 이후, 빨간색)
ax.bar(
    data_2023["Date"],
    data_2023["Term Premium Chg Std"],
    width=50,
    color="red",
)  # color="red" 추가

# x축 범위를 2023년 이후로 제한 (이미 필터링되었으므로 불필요)
# ax.set_xlim(pd.Timestamp("2023-01-01"), data_2023["Date"].max())

# x축, y축, 제목 설정
ax.set_xlabel("Date", fontsize=25)
ax.set_ylabel("Standardized Term Premium Change", fontsize=25)
ax.set_title("Standardized Term Premium Change since 2023", fontsize=25)

# x축, y축 tick 크기 조정
ax.tick_params(axis="x", labelsize=25)
ax.tick_params(axis="y", labelsize=25)

# x축 레이블 회전 및 정렬
plt.xticks(rotation=45, ha="right")

# 그리드 추가
ax.grid(True)

plt.tight_layout()
plt.show()







import blpapi
import pandas as pd
import datetime
import sys
from xlsxwriter import Workbook

oppor = "C:/Users/westl/PycharmProjects/pythonProject/oppor.xlsx"
clustering = "C:/Users/westl/PycharmProjects/pythonProject/Clustering.xlsx"


pr_res = pd.read_excel(oppor, sheet_name=0, parse_dates=True)
pr_res = pr_res[pr_res['date'] >= "2013-01-01"]

Index_list1 = pr_res.columns

pr = pd.read_excel(oppor, sheet_name=1, parse_dates=True)
pr = pr[pr['date'] >= "2013-01-01"]

Index_list2 = pr.columns


Index_list1 = [ticker for ticker in Index_list1 if ticker.lower() != 'date']
Index_list2 = [ticker for ticker in Index_list2 if ticker.lower() != 'date']


def start_session():
    session_options = blpapi.SessionOptions()
    session_options.setServerHost('localhost')
    session_options.setServerPort(8194)

    session = blpapi.Session(session_options)
    if not session.start():
        print("Failed to start session.")
        return None
    if not session.openService("//blp/refdata"):
        print("Failed to open //blp/refdata")
        return None
    return session


def fetch_data(session, tickers, fields, start_date, end_date, overrides=None):
    ref_data_service = session.getService("//blp/refdata")
    all_data = []

    for ticker in tickers:
        request = ref_data_service.createRequest("HistoricalDataRequest")
        request.getElement("securities").appendValue(ticker)
        for field in fields:
            request.getElement("fields").appendValue(field)
        request.set("startDate", start_date)
        request.set("endDate", end_date)
        request.set("periodicitySelection", "DAILY")

        # 옵션 설정 추가
        request.set("adjustmentNormal", True)
        request.set("adjustmentAbnormal", True)
        request.set("adjustmentSplit", True)

        if overrides:
            overrides_element = request.getElement("overrides")
            for override_field, override_value in overrides.items():
                override = overrides_element.appendElement()
                override.setElement("fieldId", override_field)
                override.setElement("value", override_value)

        session.sendRequest(request)

        while True:
            ev = session.nextEvent()
            for msg in ev:
                if msg.hasElement("securityData"):
                    security_data = msg.getElement("securityData")
                    ticker_name = security_data.getElementAsString("security")
                    field_data = security_data.getElement("fieldData")
                    for i in range(field_data.numValues()):
                        data_point = field_data.getValueAsElement(i)
                        date = data_point.getElementAsDatetime("date")
                        datapoint_dict = {"date": date, "Ticker": ticker_name}
                        for field in fields:
                            if data_point.hasElement(field):
                                datapoint_dict[field] = data_point.getElementAsFloat(field)
                            else:
                                datapoint_dict[field] = None  # 데이터가 없을 경우 None으로 설정
                        all_data.append(datapoint_dict)
                if msg.hasElement("responseError"):
                    error_msg = msg.getElement("responseError").getElementAsString("message")
                    print("Response Error:", error_msg, file=sys.stderr)
                if msg.hasElement("securityError"):
                    error_msg = msg.getElement("securityError").getElementAsString("message")
                    print("Security Error:", error_msg, file=sys.stderr)
            if ev.eventType() == blpapi.Event.RESPONSE:
                break

    return all_data


def fill_missing_data(df, field_name, last_date):
    if 'Ticker' not in df.columns:
        print("DataFrame columns:", df.columns)
        raise KeyError("'Ticker' column not found in the DataFrame")

    # 모든 Ticker의 모든 Date에 대해 데이터가 존재하도록 보장
    all_dates = pd.date_range(start=df['date'].min(), end=last_date)
    all_tickers = df['Ticker'].unique()

    # 인덱스 생성 시 데이터 유형을 확인하여 MultiIndex 생성
    full_index = pd.MultiIndex.from_product([all_dates, all_tickers], names=['date', 'Ticker'])
    df = df.set_index(['date', 'Ticker']).reindex(full_index).reset_index()

    # 지정된 필드의 결측값을 이전 값으로 채우기 (각 티커별로 처리)
    df[field_name] = df.groupby('Ticker')[field_name].ffill()

    # 마지막 날짜까지 최신 데이터로 채우기 (bfill로 처리)
    df[field_name] = df.groupby('Ticker')[field_name].bfill()

    return df

def save_to_excel(data_dict, filename, ticker_order, end_date):
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        for sheet_name, data in data_dict.items():
            df = pd.DataFrame(data)
            print(f"Processing sheet: {sheet_name}")
            print(df.head())  # 데이터 확인을 위해 추가
            if not df.empty:
                if sheet_name != "SPX Index":
                    df = fill_missing_data(df, sheet_name, end_date)  # end_date를 last_date로 전달
                if "Ticker" in df.columns and "date" in df.columns:
                    pivot_df = df.pivot(index="date", columns="Ticker", values=sheet_name)
                    available_tickers = [ticker for ticker in ticker_order if ticker in pivot_df.columns]
                    pivot_df = pivot_df[available_tickers]  # Ticker 컬럼을 지정된 순서로 정렬
                    pivot_df.to_excel(writer, sheet_name=sheet_name)
                else:
                    df.to_excel(writer, sheet_name=sheet_name)
            if sheet_name == "SPX Index":
                # 영업일로만 필터링된 SPX Index 데이터 사용
                df = df.set_index("date")
                business_days = pd.bdate_range(start=df.index.min(), end=df.index.max())
                df = df[df.index.isin(business_days)]
                df.to_excel(writer, sheet_name=sheet_name)


def fetch_spy_data(session, start_date, end_date):
    spy_ticker = ["SPX Index"]
    spy_fields = ["PX_LAST"]
    spy_data = fetch_data(session, spy_ticker, spy_fields, start_date, end_date)

    # 디버깅을 위해 가져온 데이터 출력
    print("Raw SPY data:")
    for entry in spy_data:
        print(entry)

    for entry in spy_data:
        entry["Ticker"] = "SPX Index"  # 각 데이터 포인트에 'Ticker' 열 추가

    # SPY 데이터 프레임 생성
    spy_df = pd.DataFrame(spy_data)
    print("Fetched SPY data:")
    print(spy_df.head())  # SPY 데이터 확인

    # 날짜 형식을 datetime64로 변환
    spy_df['date'] = pd.to_datetime(spy_df['date'])

    # 미국 영업일만 포함되도록 필터링
    business_days = pd.bdate_range(start=start_date, end=end_date)
    spy_df = spy_df[spy_df['date'].isin(business_days)]
    print("Filtered SPY data:")
    print(spy_df.head())  # 필터링된 SPY 데이터 확인

    return spy_df


def print_progress_bar(iteration, total, length=50):
    percent = ("{0:.1f}").format(100 * (iteration / float(total)))
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    sys.stdout.write(f'\rProgress: |{bar}| {percent}% Complete')
    sys.stdout.flush()


def process_index_list(session, tickers, fields_dict, start_date, end_date, filename, best_overrides):
    data_dict = {}
    total_steps = len(fields_dict) + 1
    last_date = pd.to_datetime(end_date)  # end_date를 last_date로 사용

    for i, (sheet_name, fields) in enumerate(fields_dict.items(), 1):
        if sheet_name == "PX_LAST":
            data_dict[sheet_name] = fetch_data(session, tickers, fields, start_date, end_date)
        else:
            data_dict[sheet_name] = fetch_data(session, tickers, fields, start_date, end_date, overrides=best_overrides)

        # 추가된 로직: OPER_MARGIN 시트에서 결측값을 최신 데이터로 채우는 로직 적용
        if sheet_name == "OPER_MARGIN":
            df_oper_margin = pd.DataFrame(data_dict[sheet_name])
            df_oper_margin = fill_missing_data(df_oper_margin, sheet_name, last_date)
            data_dict[sheet_name] = df_oper_margin.to_dict(orient='records')

        print_progress_bar(i, total_steps)

    # Fetch SPX Index data for business days and prices
    spy_data_df = fetch_spy_data(session, start_date, end_date)
    print("SPY data after fetching and filtering:")
    print(spy_data_df.head())  # SPY 데이터 확인
    if not spy_data_df.empty:
        spy_data_df = spy_data_df.rename(columns={"PX_LAST": "SPX Index"})
        spy_data_df["Ticker"] = "SPX Index"
        spy_data_df = spy_data_df.set_index("date")
        data_dict["SPX Index"] = spy_data_df.reset_index().to_dict(orient='records')

    print_progress_bar(total_steps, total_steps)

    save_to_excel(data_dict, filename, tickers, last_date)  # end_date를 전달


def main():
    start_date = "20130101"
    end_date = datetime.datetime.today().strftime('%Y%m%d')
    best_overrides = {"BEST_FPERIOD_OVERRIDE": "1BF"}

    fields_dict = {
        "PX_LAST": ["PX_LAST"],
        "BEST_EPS": ["BEST_EPS"]

    }

    session = start_session()
    if session:
        process_index_list(session, Index_list1, fields_dict, start_date, end_date, "weekly.xlsx", best_overrides)
        #process_index_list(session, Index_list2, fields_dict, start_date, end_date, "S&P500.xlsx", best_overrides)
        session.stop()
        print("\nData collection and saving to Excel complete.")
    else:
        print("Session failed to start.")


if __name__ == "__main__":
    main()








#==============================================================================================================
