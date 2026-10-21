local lastReport = nil

local function read(label, getter)
  local ok, value = pcall(getter)
  if ok then
    return value
  end
  return nil
end

local function collectObservation()
  local report = {
    schema = "theotown-ai-observation/v1",
    source = "theotown-lua-observation-probe",
    captured_at_ms = Runtime.getTime(),
    city = {
      id = read("id", function() return City.getId() end),
      name = read("name", function() return City.getName() end),
      population = read("population", function() return City.getPeople() end),
      money = read("money", function() return City.getMoney() end),
      income = read("income", function() return City.getIncome() end),
      happiness = read("happiness", function() return City.getHappiness() end),
      active_disaster = read("disaster", function() return City.getDisaster() end),
      buildings = read("buildings", function() return City.countBuildings() end),
      roads = read("roads", function() return City.countRoads() end),
      cars = read("cars", function() return City.countCars() end),
      pipes = read("pipes", function() return City.countPipes() end),
      wires = read("wires", function() return City.countWires() end),
      residential_space = read("residential_space", function()
        return City.getResidentialSpace()
      end),
      commercial_jobs = read("commercial_jobs", function()
        return City.getCommercialJobs()
      end),
      industrial_jobs = read("industrial_jobs", function()
        return City.getIndustrialJobs()
      end)
    }
  }

  lastReport = Runtime.toJson(report)
  Debug.info(lastReport)
  Debug.toast("TheoTown AI observation captured")
end

function script:enterCity()
  collectObservation()
end

function script:leaveCity()
  lastReport = nil
end
