import fastsim

print("FASTSim version:", fastsim.__version__)

print("\nAvailable modules and attributes:")
print(dir(fastsim))

print("\nVehicle class:")
print(getattr(fastsim, "Vehicle", "Not found"))

print("\nCycle class:")
print(getattr(fastsim, "Cycle", "Not found"))