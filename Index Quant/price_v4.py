import os

# Bloomberg C SDK DLL 경로
DLL_DIR = r"C:\Users\westl\PycharmProjects\pythonProject\venv_vf\blpapi_cpp_3.25.3.1\lib"
os.add_dll_directory(DLL_DIR)      # 먼저 DLL 경로 추가

import blpapi                      # 그다음에 blpapi import

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
        "BEST_EPS": ["BEST_EPS"],
        "BEST_SALES": ["BEST_SALES"],
        "BEST_PE_RATIO": ["BEST_PE_RATIO"],
        "BEST_PEG_RATIO": ["BEST_PEG_RATIO"],
        "BEST_CALCULATED_FCF": ["BEST_CALCULATED_FCF"],
        "BEST_GROSS_MARGIN": ["BEST_GROSS_MARGIN"],
        "CUR_MKT_CAP": ["CUR_MKT_CAP"],
        "OPER_MARGIN": ["OPER_MARGIN"],
        "BEST_CAPEX": ["BEST_CAPEX"],
        "BEST_ROE": ["BEST_ROE"],
        "BEST_PX_BPS_RATIO": ["BEST_PX_BPS_RATIO"],
        "BEST_EV_TO_BEST_EBITDA":["BEST_EV_TO_BEST_EBITDA"],
        "NEWS_SENTIMENT_DAILY_AVG":["NEWS_SENTIMENT_DAILY_AVG"]
    }

    session = start_session()
    if session:
        process_index_list(session, Index_list1, fields_dict, start_date, end_date, "Index.xlsx", best_overrides)
        process_index_list(session, Index_list2, fields_dict, start_date, end_date, "S&P500.xlsx", best_overrides)
        session.stop()
        print("\nData collection and saving to Excel complete.")
    else:
        print("Session failed to start.")


if __name__ == "__main__":
    main()
