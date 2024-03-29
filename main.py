import os
import numpy as np
from dolfin import (
    parameters,
    XDMFFile,
    Expression,
    Mesh,
    MeshFunction,
    near,
    AutoSubDomain,
    ds,
    assemble,
    dx,
    cells,
)
from ufl import as_tensor, pi
from save_data import save_data
from active_shell import ActiveShell
import subprocess
import meshio
import configreader
import json

import time as ttime
start = ttime.time()


# System parameters

parameters["form_compiler"]["quadrature_degree"] = 4
parameters["allow_extrapolation"] = True


cwd = os.getcwd()
print(cwd)
# Create config object
C = configreader.Config()
config = C.read("config.conf")


output_dir = "output/"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_dir_mesh = "output/mesh/"
if not os.path.exists(output_dir_mesh):
    os.makedirs(output_dir_mesh)

output_dir_contour = "output/contour/"
if not os.path.exists(output_dir_contour):
    os.makedirs(output_dir_contour)


# Opening JSON file
with open("../../paths.json") as json_file:
    paths = json.load(json_file)

# geometry = "eighthsphere"
geometry = config["simulation"]["Geometry"]
xdmf_name = geometry + ".xdmf"


# Simulation parameters
time = 0
Time = float(config["simulation"]["Time_max"])
dt = float(config["simulation"]["timestep"])
polymerization = int(config["simulation"]["polymerization"])

remeshing_frequency = float(
    config["remeshing"]["remeshing_frequency"]
)  # remeshing every n time steps


# Physical parameteres
inital_thickness = config["parameters"]["thickness"]
thick = Expression(inital_thickness, degree=4)
mu = float(config["parameters"]["viscosity"])
zeta = float(config["parameters"]["contractility_strength"])
basal = float(config["parameters"]["contractility_basal"])
gaussian_width = float(config["parameters"]["contractility_width"])
kd = float(config["parameters"]["depolymerization"])
vp = float(config["parameters"]["polymerization"])

nu = float(config["nematics"]["coupling_parameter"])
gamma = float(config["nematics"]["rotational_viscosity"])
tau = float(config["nematics"]["nematic_relaxation_time"])
xi = float(config["nematics"]["correlation_length"])

L_ = xi*xi*gamma/tau    # elastic_frank_constant
chi =  gamma/tau        # inverse_susceptibility

print("elastic_frank_constant", L_)
print("inverse_susceptibility", chi)

Q_tensor = as_tensor([[1.0 / 6, 0.0], [0.0, 1.0 / 6]])
q_33 = -1.0 / 3

# Volume variation
dV = config["parameters"].get("volume_variation", "0")

subprocess.call(
    [
        paths["gmsh"],
        "-2",
        "-format",
        "msh2",
        "-v",
        "1",
        "../../" + geometry + ".geo",
        "-o",
        xdmf_name.replace("xdmf", "msh"),
    ]
)
msh = meshio.read(xdmf_name.replace(".xdmf", ".msh"))
meshio.write(
    xdmf_name,
    meshio.Mesh(points=msh.points, cells={"triangle": msh.cells_dict["triangle"]}),
)
mmesh = meshio.read(xdmf_name)
mesh = Mesh()
with XDMFFile(xdmf_name) as mesh_file:
    mesh_file.read(mesh)


def radius(problem):
    # Furrow radius
    boundary_subdomains = MeshFunction(
        "size_t", problem.mesh, problem.mesh.topology().dim() - 1
    )
    boundary_subdomains.set_all(0)
    boundary_y = lambda x, on_boundary: near(x[1], 0.0, 1.0e-3) and on_boundary
    AutoSubDomain(boundary_y).mark(boundary_subdomains, 1)
    dss = ds(subdomain_data=boundary_subdomains)
    return assemble((2.0 / pi) * dss(1)(domain=problem.mesh))





initial_volume = assemble(1.0 * dx(domain=mesh)) / 3
print("Initial volume:", initial_volume)


current_radius = 1.0


filename = output_dir + xdmf_name.replace(".xdmf", "_results.xdmf")
problem = ActiveShell(
    mesh,
    mmesh,
    thick=thick,
    mu=mu,
    basal=basal,
    zeta=zeta,
    gaussian_width=gaussian_width,
    kd=kd,
    vp=vp,
    nu_=nu,
    gamma_=gamma,
    L_=L_,
    chi_=chi, 
    Q_tensor=Q_tensor,
    q_33=q_33,
    dt=dt,
    vol_ini=initial_volume,
    paths=paths,
    dV=dV,
    fname=filename,
)

hdr = "time, current_volume , current_radius, membrane_total_dissipation, membrane_passive_dissipation, membrane_active_dissipation, membrane_polymerization_dissipation, bending_total_dissipation, bending_passive_dissipation, bending_active_dissipation, bending_polymerization, dissipation_shear, furrow_thickness"

f = open("output/Data.csv", "w")
np.savetxt(f, [], header=hdr)

problem.write(
    time,
    u=True,
    beta=True,
    phi=True,
    frame=True,
    epaisseur=True,
    activity=True,
    energies=True,
)
i = 0

problem.write_mesh_from_xdmf(i)

radius_old = 1.0
d_radius = 1
while time < Time:
    i += 1
    print("Iteration {}. Time step : {}".format(i, dt))

    problem.initialize()

    niter, _ = problem.solve()

    problem.evolution(dt)
    current_radius = radius(problem)
    d_radius = abs(current_radius - radius_old)
    print("Variation in radius: {}".format(d_radius))
    radius_old = current_radius
    
    # cwd = os.getcwd()
    # print(cwd)
    # write_mesh_from_xdmf(i)
    
    if i>= 1:
        # print(problem.mesh.geometry().dim())
        dofmap_ = problem.V_thickness.tabulate_dof_coordinates()
        # print("This is thickness",problem.Q_field.vector()[:])
        # print(len(problem.Q_field.vector()[:]))

        # # ind_t = np.where()
        # print(len(dofmap_))

        # print("this is dofmap_", dofmap_)

        dofmap = problem.V_thickness.dofmap()
        nvertices = problem.mesh.ufl_cell().num_vertices()

        # Set up a vertex_2_dof list
        indices = [dofmap.tabulate_entity_dofs(0, i)[0] for i in range(nvertices)]

        vertex_2_dof = dict()
        [vertex_2_dof.update(dict(vd for vd in zip(cell.entities(0),
                                        dofmap.cell_dofs(cell.index())[indices])))
                        for cell in cells(problem.mesh)]
        

        # print("Num num_vertices = ",nvertices)
        X = problem.mesh.coordinates()

        # Set the vertex coordinate you want to modify
        xcoord, ycoord, zcoord = 0., 1., 0.
        tol = problem.mesh.rmin()
        tol = 1e-2
        # Find the matching vertex (if it exists)
        vertex_idx = []
        x_2D = []
        y_2D = []
        # Getting the 2D contour
        for idx, x in enumerate(X):
            # print(idx,x)
            if abs(x[2]-zcoord )<tol:
                x_2D = np.append(x_2D,x[0])
                y_2D = np.append(y_2D,x[1])


            # if (abs(x[0]-xcoord)<tol and abs(x[1] - ycoord) <tol and abs(x[2]-zcoord )<tol):
            #     vertex_idx = np.append(vertex_idx,idx)
            #     print("Here's the vertex", vertex_idx)

        # vertex_idx = np.where((X == (xcoord,ycoord, zcoord)).all(axis = 0))[0]
        # vertex_idx = vertex_idx[0]
        # print(x_2D, y_2D)        
        np.savetxt("output/contour/"+str(i)+".txt", np.column_stack((x_2D,y_2D)), delimiter = ";")
         
        # try:
        #     dof_idx = vertex_2_dof[vertex_idx[0]]
        #     print(dof_idx)
        #     problem.Q_field.vector()[dof_idx] = 100.
        #     problem.thickness.vector()[dof_idx] = 1.
        #     x=1
        # except:
        #     print('No matching vertex!')


        # print(X)

        # break
    problem.write(
        time + dt,
        u=True,
        beta=True,
        phi=True,
        frame=True,
        epaisseur=True,
        activity=True,
        energies=True,
    )
    if i%2==0:
        problem.write_mesh_from_xdmf(i)
    print(
        "rmin={}, rmax={}, hmin={}, hmax={}".format(
            problem.mesh.rmin(),
            problem.mesh.rmax(),
            problem.mesh.hmin(),
            problem.mesh.hmax(),
        )
    )

    save_data(f, time, problem)
    time += dt

    if i % remeshing_frequency == 0:
        if problem.mesh.rmin() < 1.5e-3:
            problem.mesh_refinement("hsiz")
            print("Uniform mesh!")
        else:
            problem.mesh_refinement("hausd")
            print("Hausdorff distance")

    if (
        current_radius < 0.25 or d_radius < 2.e-6
    ):  # If the furrow radius is smaller than twice the thickness it means that it should have stopped dividing!
        problem.write(
            time + dt,
            u=True,
            beta=True,
            phi=True,
            frame=True,
            epaisseur=True,
            activity=True,
            energies=False,
        )
        break


f.close()

r=open('output/final_radius.csv','w')

np.savetxt(r, np.column_stack((zeta,radius(problem))),delimiter=',')
r.close()
print("It ended at iteration {}, and Time {}".format(i, time))

end = ttime.time()
print("total time: ", end - start)
