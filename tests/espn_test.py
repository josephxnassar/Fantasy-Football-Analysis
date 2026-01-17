import pandas as pd

from bs4 import BeautifulSoup

from pytest_mock import MockerFixture

from backend.depth_chart.espn import ESPNDepthChart

def test_get_soup_success(mocker: MockerFixture):
    mock_response = mocker.Mock()
    mock_response.status_code = 200
    mock_response.text = "<html></html>"

    mock_get = mocker.patch("backend.depth_chart.espn.requests.get", return_value = mock_response)

    chart = ESPNDepthChart()
    soup = chart._get_soup("KC")

    mock_get.assert_called_once()
    assert isinstance(soup, BeautifulSoup)

def test_parse_soup():
    html = """
    <html>
        <body>
            <table>
                <tr><td>QB</td><td>RB</td></tr>
            </table>
            <table>
                <tbody>
                    <tr><td>Patrick Mahomes</td></tr>
                    <tr><td>Isiah Pacheco</td></tr>
                    <tr><td>Player WR1</td></tr>
                    <tr><td>Player TE1</td></tr>
                    <tr><td>Backup QB</td></tr>
                    <tr><td>Backup RB</td></tr>
                </tbody>
            </table>
        </body>
    </html>
    """

    soup = BeautifulSoup(html, "html.parser")
    chart = ESPNDepthChart()
    positions, players = chart._parse_soup(soup)

    assert positions == ["QB", "RB"]
    assert "Patrick Mahomes" in players
    assert "Isiah Pacheco" in players


def test_create_depth_chart():
    chart = ESPNDepthChart()
    
    positions = ["QB", "RB", "WR", "TE"]

    players = ["Mahomes", "QB2", "QB3", "QB4",
               "Pacheco", "RB2", "RB3", "RB4",
               "Rice",    "WR2", "WR3", "WR4",
               "Kelce",   "TE2", "TE3", "TE4"]

    df = chart._create_depth_chart(positions, players)

    assert list(df.columns) == ["Starter", "2nd", "3rd", "4th"]
    assert df.loc["QB"]["Starter"] == "Mahomes"
    assert df.loc["RB"]["2nd"] == "RB2"
    assert df.loc["WR"]["4th"] == "WR4"
    assert df.loc["TE"]["3rd"] == "TE3"

def test_run(mocker: MockerFixture):
    mock_chart = ESPNDepthChart.__new__(ESPNDepthChart)
    mock_chart.teams = ["KC", "SEA"]

    mock_soup = BeautifulSoup("<html></html>", "html.parser")

    df = pd.DataFrame({"Starter": ["Mahomes"],
                       "2nd":     ["QB2"    ],
                       "3rd":     ["QB3"    ],
                       "4th":     ["QB4"    ]}, index=["QB"])

    mocker.patch("backend.depth_chart.espn.ESPNDepthChart._get_soup", return_value = mock_soup)
    mocker.patch("backend.depth_chart.espn.ESPNDepthChart._parse_soup", return_value = (["QB"], ["Mahomes", "QB2", "QB3", "QB4"]))
    mocker.patch("backend.depth_chart.espn.ESPNDepthChart._create_depth_chart", return_value = df)

    mock_chart.run()

    result = mock_chart.cache

    assert "KC" in result
    assert "SEA" in result
    assert result["KC"].loc["QB"]["Starter"] == "Mahomes"