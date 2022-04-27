clear all
close all
data = readtable('Data.csv');

cte = 0;
% [Time, current_volume , current_radius,...
%     membrane_total_dissipation, membrane_passive_dissipation,...
%     membrane_active_dissipation, membrane_polymerization_dissipation,...
%     bending_total_dissipation, bending_passive_dissipation,...
%     bending_active_dissipation, bending_polymerization, dissipation_shear] = ...
%     data;


Time = data{:,1};
Volume = data{:,2};
Radius = data{:,3};
membrane_total_dissipation = data{:,4};
membrane_passive_dissipation = data{:,5}+1e-9;
membrane_active_dissipation = data{:,6};
membrane_polymerization_dissipation = data{:,7};
bending_total_dissipation = data{:,8};
bending_passive_dissipation = data{:,9};
bending_active_dissipation = data{:,10};
bending_polymerization = data{:,11};
shear_dissipation = data{:,12};
thickness = data{:,13};
pressure = data{:,14};


figure
plot(Time(1:end-cte), Radius(1:end-cte))
title('Furrow radius')
% figure
% % plot(Time(1:end-5), Dissipation_m(1:end-5))
% plot(Time(1:end-cte), membrane_total_dissipation(1:end-cte))
% % Total_membrane_dissipation = trapz(Time, membrane_total_dissipation)
% title('Dissipation membrane')
% 
% % figure
% plot(Time, bending_total_dissipation)
% Total_bending_dissipationc = trapz(Time, bending_total_dissipation)

% title('Dissipation bending')
% figure
% % % plot(Time(1:end-5), Dissipation_m(1:end-5))
% plot(Time(1:end-cte), membrane_passive_dissipation(1:end-cte))
% title('Passive Dissipation membrane')
% Total_membrane_passive_dissipation = trapz(Time, membrane_passive_dissipation)
% % 

% figure
% plot(Time(1:end-cte), bending_active_dissipation(1:end-cte))
% title('Active Dissipation bending')

% % Total_passive_bending_dissipation=  trapz(Time, bending_passive_dissipation) 
% 
% figure
% plot(Time(1:end-cte), membrane_polymerization_dissipation(1:end-cte))
% title('Dissipation polymerization')

% figure
% plot(Time(1:end-cte), membrane_active_dissipation(1:end-cte))
% title('Dissipation contractility')

% figure
% plot(Time(1:end-cte), membrane_polymerization_dissipation(1:end-cte))
% title('Membrane polymerization')

% figure
% plot(Time(1:end-cte), membrane_active_dissipation(1:end-cte))
% title('membrane contractility')

figure
D = ((membrane_polymerization_dissipation)+ (bending_polymerization))./((membrane_polymerization_dissipation) + (membrane_active_dissipation) + (bending_polymerization) + (bending_active_dissipation));
plot(Time(1:end-cte), D(1:end-cte))
title('Polymerization / (Polymerization + Contractility)')

% figure
% plot(Time(1:end-cte), bending_passive_dissipation(1:end-cte))
% title('Bending')

% figure
% plot(Time(1:end-cte), membrane_passive_dissipation(1:end-cte))
% title('Membrane')

figure
plot(Time(1:end-cte), ((bending_passive_dissipation(1:end-cte)>1e-9).*bending_passive_dissipation(1:end-cte)./(bending_passive_dissipation(1:end-cte) + membrane_passive_dissipation(1:end-cte))))
title('Bending / (Bending+Strechting)')


% figure
% plot(Time(1:end-cte), (bending_passive_dissipation(1:end-cte)./(+abs(bending_passive_dissipation(1:end-cte)) + abs(bending_active_dissipation(1:end-cte)))))
% title('Passive Bending / (Passive + active Bending+)')

% Phi = bending_polymerization./(bending_polymerization + membrane_polymerization_dissipation);
% figure
% plot(Time(1:end-cte), Phi(1:end-cte))
% title('Bending polym / (Bending+Strechting polymerization)')



figure
plot(Time(1:end-cte)-Time(1), Volume(1:end-cte))
% plot(Time, Radius.^3)
title('Volume')

% % 
figure
plot(Time-Time(1), thickness)

% figure
% plot(Time, - pressure)