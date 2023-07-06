import json
import requests
from typing import List
from pathlib import Path
from bs4 import BeautifulSoup
from pydantic import BaseModel

_MCC_MNC_JSON_FILE: Path = Path(__file__).parent.joinpath("mcc-mnc-table.json")


# SCHEMAS
class MCCMNCRecord(BaseModel):
    """mcc mnc record/row from mcc-mnc.com"""
    mcc: int
    mnc: int
    iso: str
    country: str
    country_code: int
    network: str


class MCCMNCRecordList(BaseModel):
    __root__: List[MCCMNCRecord]


# FETCHER
class MCCMNCFetcher:
    """fetching & parsing mcc mnc records from https://mcc-mnc.com"""
    _DOMAIN: str = "https://mcc-mnc.com/"

    @staticmethod
    def _get_mcc_mnc_site_html() -> str:
        """:return: HTML from https://mcc-mnc.com/"""
        return requests.get(MCCMNCFetcher._DOMAIN).text

    @staticmethod
    def _get_mcc_mnc_rows(html: str) -> List[List[str]]:
        """
        returns all the mcc mnc rows from https://mcc-mnc.com/
        each row is in the pattern [mcc, mnc, iso, country, country code, network]
        :param html: HTML from https://mcc-mnc.com/
        :return: list of mcc mnc rows
        """
        records = []
        soup = BeautifulSoup(html)
        table = soup.find('table', attrs={'id': 'mncmccTable'})
        table_body = table.find('tbody')
        rows = table_body.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            cols = [e.text.strip() for e in cols]
            records.append([e for e in cols if e])
        return records

    @staticmethod
    def _parse_records(mcc_mnc_rows: List[List[str]]) -> List[MCCMNCRecord]:
        """
        parsing mcc mnc rows to list of MCCMNCRecord
        :param mcc_mnc_rows: list of mcc mnc rows. row is in the pattern [mcc, mnc, iso, country, country code, network]
        :return: list of MCCMNCRecord
        """
        mcc_mnc_records: List[MCCMNCRecord] = []
        for mcc_mnc_row in mcc_mnc_rows:
            try:
                mcc_mnc_records.append(
                    MCCMNCRecord(mcc=mcc_mnc_row[0],
                                 mnc=mcc_mnc_row[1],
                                 iso=mcc_mnc_row[2],
                                 country=mcc_mnc_row[3],
                                 country_code=mcc_mnc_row[4],
                                 network=mcc_mnc_row[5])
                )
            except IndexError:
                pass  # some rows are not fully populated
        return mcc_mnc_records

    @staticmethod
    def json_file():
        """
        creating a json file(mcc-mnc-table.json) with all the mcc mnc data from https://mcc-mnc.com/
        :return: None
        """
        mcc_mnc_html: str = MCCMNCFetcher._get_mcc_mnc_site_html()
        mcc_mnc_rows: List[List[str]] = MCCMNCFetcher._get_mcc_mnc_rows(html=mcc_mnc_html)
        mcc_mnc_records: List[MCCMNCRecord] = MCCMNCFetcher._parse_records(mcc_mnc_rows=mcc_mnc_rows)
        mcc_mnc_records_list: MCCMNCRecordList = MCCMNCRecordList.parse_obj(mcc_mnc_records)
        with open(_MCC_MNC_JSON_FILE, "w") as f:
            f.write(json.dumps(mcc_mnc_records_list.dict()["__root__"], indent=2))


MCCMNCFetcher.json_file()
