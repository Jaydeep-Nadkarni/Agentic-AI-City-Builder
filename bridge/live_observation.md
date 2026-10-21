# TheoTown live observation discovery

## Evidence

The official TheoTown City module documents read functions for:

- `City.getId()` and `City.getName()`
- `City.getPeople()`
- `City.getMoney()` and `City.getIncome()`
- `City.getHappiness()`
- `City.getDisaster()`
- `City.countBuildings()`, `City.countRoads()`, `City.countCars()`
- `City.countPipes()` and `City.countWires()`
- `City.getResidentialSpace()`
- `City.getCommercialJobs()` and `City.getIndustrialJobs()`

The official Runtime module documents `Runtime.getTime()` and `Runtime.toJson()`.
These are API-level findings, not proof that every function exists in the exact
installed TheoTown build.

## Isolated proof of concept

The separate [observation probe](../plugin/observation%20probe/) contains:

- [observation.json](../plugin/observation%20probe/observation.json)
- [observer.lua](../plugin/observation%20probe/observer.lua)

It runs on `script:enterCity`, reads the documented values, converts the report
to JSON, and displays it through TheoTown's debug output/toast. It does not place
buildings, modify roads, spend money, execute commands, or call the Python
dispatcher.

Install this folder separately from the working `scripting test` plugin. In a
test city, enable scripting if required, enter the city, and inspect the debug
output. A successful probe confirms which fields are non-nil in the installed
build. A runtime error or nil field must be recorded as an experiment result,
not silently treated as a supported metric.

## Transport conclusion

The documented storage APIs are game-managed persistence, not arbitrary host
filesystem access. The documented command API returns feedback inside TheoTown,
not to an external process. The official module reference does not document
HTTP, TCP/UDP sockets, or a Python bridge. Therefore this probe currently
demonstrates in-game observation only; it does not establish a Python transport.
