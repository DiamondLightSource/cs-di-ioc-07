[![CI](https://github.com/DiamondLightSource/cs-di-ioc-07/actions/workflows/ci.yml/badge.svg)](https://github.com/DiamondLightSource/cs-di-ioc-07/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/DiamondLightSource/cs-di-ioc-07/branch/main/graph/badge.svg)](https://codecov.io/gh/DiamondLightSource/cs-di-ioc-07)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

# rf_postmortem

RF and BPM Postmortem Backend


What            | Where
:---:           | :---:
Source          | <https://github.com/DiamondLightSource/cs-di-ioc-07>
Docker          | `docker run ghcr.io/diamondlightsource/cs-di-ioc-07:latest`
Releases        | <https://github.com/DiamondLightSource/cs-di-ioc-07/releases>


## Running

Run as follows:

```
python -m rf_postmortem
```

The flag `-d` can be used to run in debug mode.


### Testing plotting

To test the plotting functionality, run the following command:

```
python -m rf_postmortem.plotserv
```
