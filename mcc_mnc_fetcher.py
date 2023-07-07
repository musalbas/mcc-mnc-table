"""
This module can be used to fetch & parse mcc, mnc data from https://mcc-mnc.com
Usage:
    from mcc_mnc_fetcher import MCCMNCFetcher
    MCCMNCFetcher.json_file()  # creates mcc-mnc-table.json
    MCCMNCFetcher.csv_file()   # creates mcc-mnc-table.cxv
    MCCMNCFetcher.xml_file()   # creates mcc-mnc-table.xml
"""
import csv
import json
import requests
import xml.etree.ElementTree as ET
from typing import List
from pathlib import Path
from xml.dom import minidom
from bs4 import BeautifulSoup
from pydantic import BaseModel

_MCC_MNC_FILE: Path = Path(__file__).parent.joinpath("mcc-mnc-table")


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
    def json_file() -> None:
        """
        creating a json file(mcc-mnc-table.json) with all the mcc mnc data from https://mcc-mnc.com/
        :return: None
        """
        mcc_mnc_html: str = MCCMNCFetcher._get_mcc_mnc_site_html()
        mcc_mnc_rows: List[List[str]] = MCCMNCFetcher._get_mcc_mnc_rows(html=mcc_mnc_html)
        mcc_mnc_records: List[MCCMNCRecord] = MCCMNCFetcher._parse_records(mcc_mnc_rows=mcc_mnc_rows)
        mcc_mnc_records_list: MCCMNCRecordList = MCCMNCRecordList.parse_obj(mcc_mnc_records)
        with open(f"{_MCC_MNC_FILE}.json", "w") as f:
            f.write(json.dumps(mcc_mnc_records_list.dict()["__root__"], indent=2))

    @staticmethod
    def csv_file() -> None:
        """
        creating a csv file(mcc-mnc-table.csv) with all the mcc mnc data from https://mcc-mnc.com/
        :return: None
        """
        mcc_mnc_html: str = MCCMNCFetcher._get_mcc_mnc_site_html()
        mcc_mnc_rows: List[List[str]] = MCCMNCFetcher._get_mcc_mnc_rows(html=mcc_mnc_html)
        with open(f"{_MCC_MNC_FILE}.csv", "w", newline="") as f:
            csv_writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for mcc_mnc_row in mcc_mnc_rows:
                csv_writer.writerow(mcc_mnc_row)

    @staticmethod
    def xml_file() -> None:
        """
        creating a xml file(mcc-mnc-table.xml) with all the mcc mnc data from https://mcc-mnc.com/
        :return: None
        """
        mcc_mnc_html: str = MCCMNCFetcher._get_mcc_mnc_site_html()
        mcc_mnc_row_pattern = ["mcc", "mnc", "iso", "country", "country_code", "network"]
        mcc_mnc_rows: List[List[str]] = MCCMNCFetcher._get_mcc_mnc_rows(html=mcc_mnc_html)
        root_tag = ET.Element('records')
        for mcc_mnc_row in mcc_mnc_rows:
            record_tag = ET.SubElement(root_tag, 'record')
            for index, value in enumerate(mcc_mnc_row):
                vary_tag = ET.SubElement(record_tag, mcc_mnc_row_pattern[index])
                vary_tag.text = value
        xml_string = minidom.parseString(ET.tostring(root_tag)).toprettyxml()
        with open(f"{_MCC_MNC_FILE}.xml", "w") as f:
            f.write(xml_string)


if __name__ == '__main__':
    MCCMNCFetcher.json_file()
    MCCMNCFetcher.csv_file()
    MCCMNCFetcher.xml_file()
