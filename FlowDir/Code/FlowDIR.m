function [] = FlowDIR(volcano, dem, SWlength, craterX_temp, craterY_temp, buff, thr, uncertainty, uncertM, ts_save, varargin)
%% FlowDIR provides a probabilistic forecast of the directionality of topographically controlled hazardous flows
% It can be run through the command line or using pop-up GUIs that guide with input parameterisation 
% To run with the GUI interface type 'FlowDIR' into the matlab command window and
% follow the instructions. Alternatively for the command line
% implementation type FlowDIR(input arguments) 
% e.g. FlowDIR('Semeru', 'semeru_srtm.tif', 300, 712094, 9102751, 50, 60, 1, 50, 30000)

%______________________________________________________________________________________________________________________________________________________________________________________________________________
%% Required input arguments:
%
%       volcano:            The name of the volcano                   e.g. 'Shinmoedake'
%       dem:                Digital elevation model filename          e.g. 'Shinmoedake_2016_15m.tif'       
%       SWlength:           Maximum swath length in metres. This should be large enough to extend out of the summit crater/region.
%       craterX_temp:       The X coordinate of the start point.
%       craterY_temp:       The Y coordinate of the start point.
%       buff:               Length of the buffer zone in metres.
%       thr:                Elevation gain threshold in meters. FlowDIR calculates whether the along swath elevation gain is above the threshold.
%       uncertainty:        Choose whether uncertainty in the start point is included. Input 0/1.     
%       uncertM:            If uncertainty = 1, quantify the size of the initialisation polygon in m. This should be a multiple of the DEM resolution
%       ts_save:            Timestep for least cost path save
%______________________________________________________________________________________________________________________________________________________________________________________________________________
% Written by Elly Tennant 2020-22

close all,
tic
warning('off','all')

    %% Set up input dialogue
    
if nargin == 0 %(Interactive mode with GUIs)
prompt = {'Volcano name:','DEM file:','Swath length:', 'Buffer (m)', 'Elevation threshold (m):',...
  'Capture uncertainty in start? (0/1)', 'Start uncertainty (m)', 'Save least cost path every N steps (input N)'};
dlgtitle = 'FlowDIR inputs'; dims = [1 50];
definput = {'Shinmoedake','Shinmoedake_2016_5m_clip.tif','800', '50','30', '1', '50', '3000'};
inputs = inputdlg(prompt,dlgtitle,dims,definput);

 
volcano = inputs{1};
dem = inputs{2};
SWlength = str2double(inputs(3));
buff = str2double(inputs(4));
thr = str2double(inputs(5));
uncertainty = str2double(inputs(6));
uncertM = str2double(inputs(7));
ts_save = str2double(inputs(8));
 
 end

% 
% volcano = 'Semeru';
% dem = 'Semeru.tif';
% SWlength = 300;
% buff = 50;
% thr = 60;
% uncertainty = 1;
% uncertM = 50;
% ts_save = 30000;
% craterX_temp = 712094;
% craterY_temp =   9102751; 

 
 DEM = GRIDobj(dem);

if nargin == 0 %(Interactive mode with GUIs)
waitfor(msgbox('Plotting DEM...draw a polygon to clip, double click inside when finished'))
MASK = createmask(DEM, 'usehillshade'); % option to clip the DEM
DEM = crop(DEM,MASK,NaN);
title('Click +/- to zoom in/out')
waitfor(msgbox('Click again for start point'))
[craterX_temp, craterY_temp] = ginput(1);
end

close all

if not(isfolder(sprintf('%s/%s','Out', volcano)))
    mkdir(sprintf('%s/%s','Out', volcano))
end

if not(isfolder(sprintf('%s/%s/%d', 'Out', volcano, 0)))
    mkdir(sprintf('%s/%s/%d', 'Out', volcano, 0))
end


runs = dir(sprintf('%s/%s', 'Out', volcano));
r = struct2cell(runs);
r_temp = r(1,:);
r_db = str2double(r_temp);
maxr = max(r_db);

mkdir(sprintf('%s/%s/%d', 'Out', volcano, maxr+1))


swath_nb = 360;
% Set the binwidth (number of degrees) to interpolate azimuths to. 22.5 is
% the default and is centered on north
interp_to = 22.5; 
swL = SWlength;

% Make DEM x and y matrices
DEM_xcells = linspace(DEM.refmat(3,1), DEM.refmat(3,1)+size(DEM.Z,2)*DEM.refmat(2,1),size(DEM.Z,2)+1);
DEM_ycells = linspace((DEM.refmat(3,2)-size(DEM.Z,1)*DEM.refmat(2,1)),DEM.refmat(3,2), size(DEM.Z,1)+1);
DEM_ycells = flip(DEM_ycells);
DEM_xcells = DEM_xcells(1:end-1);
DEM_ycells = DEM_ycells(1:end-1);
res = DEM.cellsize;
% meshgrid
[dem_xcells, dem_ycells] = meshgrid(DEM_xcells, DEM_ycells);
%dem_ycells = flip(dem_ycells);

% snap the input starting coordinate to the nearest DEM cell centre
[val,idx] = min(abs(craterX_temp-DEM_xcells));
craterX_temp  = DEM_xcells(idx);

[val,idy] = min(abs(craterY_temp-DEM_ycells));
craterY_temp  = DEM_ycells(idy);

hold on

scatter(craterX_temp, craterY_temp, 'rx')


    %% Generate initialisation polygon
% generate polygon for the case of uncertainty = 1    
nbcells = uncertM/round(DEM.cellsize) ; nbcells = round(nbcells);
% The polygon must be at least one DEM cell away from the starting point
if(nbcells <1)==1
nbcells = 1;
end
vertx = [DEM_xcells(idx-nbcells) DEM_xcells(idx-nbcells) DEM_xcells(idx+nbcells) DEM_xcells(idx+nbcells) ];
verty = [DEM_ycells(idy+nbcells) DEM_ycells(idy-nbcells) DEM_ycells(idy-nbcells) DEM_ycells(idy+nbcells) ];
polyout = polyshape(vertx, verty);
%plot(polyout)

% generate polygon for the case of uncertainty = 0
if uncertainty == 0;
     vertx = [DEM_xcells(idx-1) DEM_xcells(idx-1) DEM_xcells(idx+1) DEM_xcells(idx+1) ];
    verty = [DEM_ycells(idy+1) DEM_ycells(idy-1) DEM_ycells(idy-1) DEM_ycells(idy+1) ];

    polyout = polyshape(vertx, verty);       
end 

% Get the coordinates of the cells that are in the polygon
[in,on] = inpolygon(dem_xcells,dem_ycells,polyout.Vertices(:,1),polyout.Vertices(:,2));


fprintf('%s\n', 'Running FlowDir, please wait...' );

xcells = dem_xcells(in); ycells = dem_ycells(in);
%% Setup storage space 
% Store tables output for each point in stage 1.
T_all = cell(length(xcells),1); 

% here is where we will store the cells that are hit for any given run, the
% third dimension corresponds to the initialisation point
new_mat = nan(size(DEM.Z,1),size(DEM.Z,2));
new_mat_all = nan(size(DEM.Z,1),size(DEM.Z,2),length(xcells));

% heres where we will store the number of steps
nb_steps_all =nan(size(DEM.Z,1),size(DEM.Z,2),length(xcells));

% reorder the initialisation point coordinates so that the starting
% coordinate is run first, so that it can be used to make the buffer. 
idmid = (length(xcells)+1)/2;
xcells = [craterX_temp; xcells(1:idmid-1); xcells(idmid+1:end)];
ycells = [craterY_temp; ycells(1:idmid-1); ycells(idmid+1:end)];

%% Calculate the buffer limit for the starting coordinate

fprintf('%s', 'Calculating buffer...')
craterX = xcells(1); craterY = ycells(1);
% Setup swaths radiating from start point, each swath will have 2 pixels width.
swath_width = DEM.cellsize.*2;
% Generate azimuths
angles = linspace(0, 359, swath_nb); 
% Get coords points on a circle (radius = swL) for each angle
    x = swL * cosd(angles) + craterX; 
    y = swL * sind(angles) + craterY;

    % Correct radians to geographic azimuth
    tmp = zeros(swath_nb,1); 
    
        for iS = 1:swath_nb
        tmp(iS) = 90-(iS-1)*(swath_nb/360);
        end
        
    % If less than zero add 360 to make positive 
    tmp(tmp<0) = tmp(tmp<0)+360;
    [~, angleIdx] = sort(tmp);
    
    % x and y are now points on a clockwise circle that has 1 = N
    x = x(angleIdx);
    y = y(angleIdx);

    swathSize = zeros(swath_nb, 1);

   % Make swaths

     for iS = 1:swath_nb
        
     % Create swath from centre to each point
        SW = SWATHobj(DEM, [craterX, x(iS)], [craterY, y(iS)], 'width', swath_width);

        Z = SW.Z;
        X = SW.X(round(size(SW.X,1)/2),:);
        Y = SW.Y(round(size(SW.Y,1)/2),:);
    
        % DEM quality check: find values where elevation is <=0
        checkElev = find(Z<=0, 1);
            if isempty(checkElev)== 0
                waitfor(msgbox('Swaths exist with elevation values <= 0 m, check the DEM', 'Error', 'error'));
                error('Swaths exist with elevation values <= 0 m, check the DEM');
            end
    
        % Take the mean of the pixels across the width, to smooth irregularities in the DEM
        swath = mean(SW.Z,1); 
    
            % Load the first swath to set the size of the storage matrix
            if iS == 1
                swathAll = zeros(length(swath), swath_nb);
            end
             
        % Handle swaths of different sizes
            if length(swath) == size(swathAll,1)
                swathAll(:, iS) = swath';
                elseif length(swath) < size(swathAll,1)
                swathAll(1:length(swath), iS) = swath';
            else
                swathAll(:, iS) = swath(1:size(swathAll,1));
            end
                
        % Do the same for X and Y coordinates of swath
            if iS == 1
            X_all = zeros(length(swath), swath_nb);
            Y_all = zeros(length(swath), swath_nb);
            end
        if length(swath) == size(X_all,1)
            X_all(:, iS) = X';
            Y_all(:, iS) = Y';
            elseif length(swath) < size(X_all,1)
            X_all(1:length(swath), iS) = X';
            Y_all(1:length(swath), iS) = Y';
        else
            X_all(:, iS) = X(1:size(swathAll,1));
            Y_all(:, iS) = Y(1:size(swathAll,1));

        end

        end

    % Identify crater edges

    % For each azimuth find the maximum elevation along the swath, and clip the
    % swath using this
    swathAll_clip = zeros(size(swathAll));
    X_all_clip = zeros(size(swathAll));
    Y_all_clip = zeros(size(swathAll));
    
    % convert user input buffer to number of cells
    b = round(buff/DEM.cellsize);

    idMax_all = [];

        for i = 1:swath_nb
            sw = swathAll(:,i);
            maximum = max(sw);
            idMax = find(sw == maximum);
            idMax = max(idMax); %incase two cells have the same value
            idMax_all = [idMax_all, idMax];
            % if the max id is the final value in the swath dont apply the
            % buffer
            if idMax+b >= size(swathAll,1)
                swathAll_clip(1:idMax,i) = swathAll(1:idMax,i);
                X_all_clip(1:idMax,i) = X_all(1:idMax,i);
                Y_all_clip(1:idMax,i) = Y_all(1:idMax,i);

            else %idMax+b < size(swathAll,1)
                swathAll_clip(1:idMax+b,i) = swathAll(1:idMax+b,i);
                X_all_clip(1:idMax+b,i) = X_all(1:idMax+b,i);
                Y_all_clip(1:idMax+b,i) = Y_all(1:idMax+b,i);
            end
        
        end


     

    swathAll_clip(swathAll_clip == 0)= NaN;

    X_all_clip(X_all_clip == 0)= NaN;
    Y_all_clip(Y_all_clip == 0)= NaN;
    
    x_all = zeros(1,360); y_all = zeros(1,360);
    elev_all = zeros(1,360); id_clip_all = zeros(1,360);

        for i = 1:swath_nb
            id_clip = max(find(isnan(X_all_clip(:,i)) == 0));
            hold on
            id_clip_all(i) = id_clip;
            x_all(i) = X_all_clip(id_clip,i);
            y_all(i) = Y_all_clip(id_clip,i);
            elev_all(i) = swathAll_clip(id_clip,i);
        end
    
    hold on

plot(x_all,y_all, 'k')

% check that all of the initialisation points are inside the crater buffer
% polygon, if we have a breached crater and a smaller buffer is used this
% might not be the case.
buffer_poly = polyshape(x_all, y_all);
% find the azimuths where the initialisation points are outside of the
% uncertainty polygon
[in,on] = inpolygon(x_all,y_all,polyout.Vertices(:,1), polyout.Vertices(:,2));

% if there are points where this is the case...extend the buffer in these
% directions
if max(max(in))==1
waitfor(msgbox(['Warning...some of the intialisation points are outside of the buffer, either cancel the simulation and reconsider inputs, or click ok to double the buffer width in these directions.']))
scatter(x_all(in), y_all(in), 'bx')
% get the ids for these cells
azToExtend = find(in==1);

% extend the buffer limit outwards in these directions. Its extended by the
% size of the initialisation polygon agin. 
for i = 1:length(azToExtend)
    az = azToExtend(i);
    id_clip_all(az) = id_clip_all(az)+round(nbcells);
end

X_all_clip = X_all; Y_all_clip = Y_all;
% reclip the swaths
for i = 1:swath_nb
    X_all_clip(id_clip_all(i)+1:end,i) = 0;
    Y_all_clip(id_clip_all(i)+1:end,i) = 0;
    x_all(i) = X_all_clip(id_clip_all(i),i);
    y_all(i) = Y_all_clip(id_clip_all(i),i);
   
end

buffer_poly = polyshape(x_all, y_all);

end


plot(x_all, y_all)
[in,on] = inpolygon(dem_xcells,dem_ycells,buffer_poly.Vertices(:,1),buffer_poly.Vertices(:,2));

buffmat = nan(size(DEM.Z));
% chnage all values outside buffer to 10k, to be used to stop simulation.
buffmat(in==0)=10000;


%% Run flowDIR for all initialisation points

  % If uncertainty = 1, use all cells inside and on the polygon  
for coord = 1:length(xcells) % for all start points

    swathAll_clip = zeros(size(swathAll));
    X_all_clip = zeros(size(swathAll));
    Y_all_clip = zeros(size(swathAll));
    
    fprintf('%s[%d%s%d]%s\n', 'Start point # ', coord, '/', length(xcells), '...'); 
  
    craterX = xcells(coord); craterY = ycells(coord);

    % Get coords points on a circle (radius = swL) for each angle
    x = swL * cosd(angles) + craterX; 
    y = swL * sind(angles) + craterY;

    % Correct radians to geographic azimuth
    tmp = zeros(swath_nb,1); 
    
        for iS = 1:swath_nb
        tmp(iS) = 90-(iS-1)*(swath_nb/360);
        end
        
    % If less than zero add 360 to make positive 
    tmp(tmp<0) = tmp(tmp<0)+360;
    [~, angleIdx] = sort(tmp);
    
    % x and y are now points on a clockwise circle that has 1 = N
    x = x(angleIdx);
    y = y(angleIdx);

    swathSize = zeros(swath_nb, 1);

           %% Make swaths

     for iS = 1:swath_nb
        
     % Create swath from centre to each point
        SW = SWATHobj(DEM, [craterX, x(iS)], [craterY, y(iS)], 'width', swath_width);

        Z = SW.Z;
        X = SW.X(round(size(SW.X,1)/2),:);
        Y = SW.Y(round(size(SW.Y,1)/2),:);
    
        % DEM quality check: find values where elevation is <=0
        checkElev = find(Z<=0, 1);
            if isempty(checkElev)== 0
                waitfor(msgbox('Swaths exist with elevation values <= 0 m, check the DEM', 'Error', 'error'));
                error('Swaths exist with elevation values <= 0 m, check the DEM');
            end
    
        % Take the mean of the pixels across the width, to smooth irregularities in the DEM
        swath = mean(SW.Z,1); 
    
            % Load the first swath to set the size of the storage matrix
            if iS == 1
                swathAll = zeros(length(swath), swath_nb);
            end
             
        % Handle swaths of different sizes
            if length(swath) == size(swathAll,1)
                swathAll(:, iS) = swath';
                elseif length(swath) < size(swathAll,1)
                swathAll(1:length(swath), iS) = swath';
            else
                swathAll(:, iS) = swath(1:size(swathAll,1));
            end
                
        % Do the same for X and Y coordinates of swath
            if iS == 1
            X_all = zeros(length(swath), swath_nb);
            Y_all = zeros(length(swath), swath_nb);
            end
        if length(swath) == size(X_all,1)
            X_all(:, iS) = X';
            Y_all(:, iS) = Y';
            elseif length(swath) < size(X_all,1)
            X_all(1:length(swath), iS) = X';
            Y_all(1:length(swath), iS) = Y';
        else
            X_all(:, iS) = X(1:size(swathAll,1));
            Y_all(:, iS) = Y(1:size(swathAll,1));

        end

        end

% clip using the polygon buffer generated using first initialisation point        
[in,on] = inpolygon(X_all,Y_all,buffer_poly.Vertices(:,1),buffer_poly.Vertices(:,2));
%X_all_clip = X_all(in); Y_all_clip = Y_all(in); %swathAll_clip = swathAll(swathAll(in));


for i = 1:swath_nb
lngth = sum(in(:,i));
EC(i) = swathAll(lngth,i)-swathAll(1,i);
end

    LL = ((interp_to/2:interp_to:swath_nb))';
    UL = ((LL+interp_to)-1);
    UL(end) = LL(1)-1;

    mid = (LL+UL)/2; mid(end) = 360;

        for i = 1:length(LL)
            interpEC(i) = mean(EC(LL(i):UL(i))); % find the mean for each bin
            
                if LL(i) > UL(i) % Wrap around the bin edges
                    interpEC(i) = mean([EC(LL(i):end), EC(1:UL(i))]);
                end    
        end
    
    T = table(LL, UL, mid, interpEC');
    T = renamevars(T,'Var4','interpEC');
    
    % Invert so that high values are the most likely travel direction
    T.inv_interpEC = max(T.interpEC)-T.interpEC;
    % Sum all of the inverse  values
    tot_SUM = sum(T.inv_interpEC);
    % Find the percentage of the total sum
    T.prob = (T.inv_interpEC/tot_SUM)*100;
    save('Table_strt_1', 'T');
%    save(sprintf('%s/%s/%d/%s', 'Out', volcano, maxr+1, 'workspace'))
   
    % Identify elevation change above threshold, use this to set marker size
    T.isBelow = T.interpEC < thr;
    T.isAbove = T.interpEC >= thr;
    T.size(T.isBelow) = 1;
    T.size(T.isAbove) = 5;

    T_all{coord} = T; % One table is generated per start point

    %% 2)  Least cost path calculation
% we will use this as our elevation matrix
 mat = DEM.Z;

 % res = DEM.cellsize;

% here is where we will store the cells that are hit for any given run
 new_mat = nan(size(mat));

% here is where we will store the ids of the cells that are hit
i_all = []; j_all = [];

% here is where we will store the step number which can be used to trace
% the progress of the simulation
nb_steps = nan(size(mat));
        
% % find the id in the DEM matrix of the start cell
% [~, i] = min(abs(craterX-DEM_xcells)); % i is for the x direction (cols), j is for the y direction (rows)
% [~, j] = min(abs(craterY-DEM_ycells));

%find the id in the DEM matrix of the start cell
[~, i] = min(abs(xcells(coord)-DEM_xcells)); % i is for the x direction (cols), j is for the y direction (rows)
[~, j] = min(abs(ycells(coord)-DEM_ycells));


%i = i-1; j = j-1; % Make sure we are taking the top left corner of the correct cell;



% P_buff = polybuffer(P,1);
[in,on] = inpolygon(dem_xcells,dem_ycells,buffer_poly.Vertices(:,1),buffer_poly.Vertices(:,2));
B = bwperim(in,8);
%*****

new_mat(isnan(new_mat)) = 0;

%new_mat(B==1)=100000;


% store the id of the first cell (craterxy)
i_all = [i_all; i];
j_all = [j_all; j];

% get the ids of the cells that surround the first active cell
idJ_surround = [j-1, j+1, j-1, j, j+1, j, j+1, j-1]';
idI_surround = [i, i, i+1, i+1, i+1, i-1, i-1,i-1]'; 

new_mat(j_all,i_all) = 1;
new_mat(new_mat==0) = NaN;
% pcolor(dem_xcells, dem_ycells, new_mat)
% shading flat

% nb_steps(j_all, i_all) = 1;

% Calculate the gradient betwen the active cell and each of the surrounding
% cells

% **** change to gradient (25th May 2023)
surround_cells = [((mat(j-1,i)-mat(j,i))/res); ((mat(j+1,i)-mat(j,i))/res); ((mat(j-1,i+1)-mat(j,i))/sqrt(2*res^2));((mat(j,i+1)-mat(j,i))/res);...
    ((mat(j+1,i+1)-mat(j,i))/sqrt(2*res^2)); ((mat(j,i-1)-mat(j,i))/res); ((mat(j+1,i-1)-mat(j,i))/sqrt(2*res^2));  ((mat(j-1,i-1)-mat(j,i))/sqrt(2*res^2))];

while length(j_all) < 30000 % this is the maximum number of steps possible. Set to a very large number as the code will stop at the buffer.

% Organise into a table
surround = table(idI_surround, idJ_surround, surround_cells);

%scatter(DEM_xcells(surround.idI_surround), DEM_ycells(surround.idJ_surround), 'bx')


% sort the table so that the lowest elevation is at the top
S_surround = sortrows(surround, 'surround_cells'); %sort the table by lowest elev value

tId = []; % space to store already traversed cells
% For each row of the table compare the i and j values to the full list to
% see if cells have already been traversed
for c = 1:height(S_surround)
    id_t = find((S_surround.idI_surround(c) == i_all(:)) & (S_surround.idJ_surround(c) == j_all(:)), 1);
     if isempty(id_t)==0
        tId = [tId, c];
     end
end

% if ALL of the table rows have been active, we need to make the table bigger 
% until we have find some cells that havent been active.This will be done
% by dilating the surrounding cells.
if numel(tId) == height(S_surround)
    % Make an empty matrix to perform the dilation on
    dil = zeros(size(new_mat));
    % assign a value of 1 to the cells that we want to dilate
    dil(S_surround.idJ_surround, S_surround.idI_surround) = 1;
    % define the structuring element, thi will be used to perform the
    % dilation
    SE = strel('square',3);
    % Make the dilated object
    dilated = imdilate(dil,SE);
    % Get the position of the new dilated cells
    [idJ_surround, idI_surround] = find(dilated==1);
    t = table(idI_surround, idJ_surround); % store ina table
    % This gives the full list of coordinates but we only want the edge cells
    % Get the edges of the shape
    tid1 = find(t.idJ_surround == min(idJ_surround));
    tid2 = find(t.idJ_surround == max(idJ_surround));
    tid3 = find(t.idI_surround == min(idI_surround));
    tid4 = find(t.idI_surround == max(idI_surround));
    tid = [tid1; tid2; tid3;tid4];
    % order this into a table
    new_t = t(tid,:);
    % delete duplicate cells
    new_t_unique = unique(new_t);
    % Get the elevation values of these cells
    new_t_surround_cells = [];
    for ss = 1:height(new_t_unique)
    new_t_surround_cells(ss) = [mat(new_t_unique.idJ_surround(ss), new_t_unique.idI_surround(ss))];
    end
    % add the elevation values to the table
    new_t_unique.surround_cells = new_t_surround_cells';
    % add these expanded cells to the table
    S_surround = [S_surround; new_t_unique];
    % check again to see if any of the cells have been active
    tId = []; % space to store already traversed cells
    % For each row of the table compare the i and j values to the full list to
    % see if cells have already been traversed
    for c = 1:height(S_surround)
        id_t = find((S_surround.idI_surround(c) == i_all(:)) & (S_surround.idJ_surround(c) == j_all(:)), 1);
        if isempty(id_t)==0
            tId = [tId, c];
        end
    end
        
            % Continue dilating the shape until non-active cells are reached.Loops
            % through dilating the output from the previous iteration.
            while numel(tId) == height(S_surround)
            % Make the dilated object
            dil = imdilate(dil,SE);
            % Get the position of the new dilated cells
            [idJ_surround, idI_surround] = find(dil==1);
            t = table(idI_surround, idJ_surround); % store ina table
            % This gives the full list of coordinates but we only want the edge cells
            % Get the edges of the shape
            tid1 = find(t.idJ_surround == min(idJ_surround));
            tid2 = find(t.idJ_surround == max(idJ_surround));
            tid3 = find(t.idI_surround == min(idI_surround));
            tid4 = find(t.idI_surround == max(idI_surround));
            tid = [tid1; tid2; tid3;tid4];
            % order this into a table
            new_t = t(tid,:);
            % delete duplicate cells
            new_t_unique = unique(new_t);
            % Get the elevation values of these cells
            for ss = 1:height(new_t_unique)
            new_t_surround_cells(ss) = [mat(new_t_unique.idJ_surround(ss), new_t_unique.idI_surround(ss))];
            end
            % add the elevation values to the table
            new_t_unique.surround_cells = new_t_surround_cells';
            % add these expanded cells to the table
            S_surround = [S_surround; new_t_unique];
            % check again to see if any of the cells have been active
            tId = []; % space to store already traversed cells
            % For each row of the table compare the i and j values to the full list to
            % see if cells have already been traversed
            for c = 1:height(S_surround)
                id_t = find((S_surround.idI_surround(c) == i_all(:)) & (S_surround.idJ_surround(c) == j_all(:)), 1);
                if isempty(id_t)==0
                    tId = [tId, c];
                end
            end
            end
            
    % delete rows that have already been active
    S_surround(tId,:) = [];
    % sort the table again by the lowest at the top
    S_surround = sortrows(S_surround, 'surround_cells'); 
    % make the lowest elevation the next active cell
    iL = S_surround.idI_surround(1);
    jL = S_surround.idJ_surround(1);
    % add the id to the list of ids
    i_all = [i_all; iL];
    j_all = [j_all; jL];

end
% % Added 2nd june to fix shinmoedake sim 12 issue
% tId = []; % space to store already traversed cells
%     % For each row of the table compare the i and j values to the full list to
%     % see if cells have already been traversed
%     for c = 1:height(S_surround)
%         id_t = find((S_surround.idI_surround(c) == i_all(:)) & (S_surround.idJ_surround(c) == j_all(:)), 1);
%         if isempty(id_t)==0
%             tId = [tId, c];
%         end
%     end
        

% if NONE of the table rows have been active the next active cell is the
% lowest elevation
if numel(tId) == 0
   iL = S_surround.idI_surround(1);
   jL = S_surround.idJ_surround(1); 
   i_all = [i_all; iL];
   j_all = [j_all; jL];
end

% Added 2nd june to fix shinmoedake sim 12 issue
tId = []; % space to store already traversed cells
    % For each row of the table compare the i and j values to the full list to
    % see if cells have already been traversed
    for c = 1:height(S_surround)
        id_t = find((S_surround.idI_surround(c) == i_all(:)) & (S_surround.idJ_surround(c) == j_all(:)), 1);
        if isempty(id_t)==0
            tId = [tId, c];
        end
    end
        

% if SOME table rows have been active, delete the rows, find the
% smallest elevation and make that the next active cell. 
if numel(tId)> 0 & numel(tId)< height(S_surround)
    %fprintf('%s', 'Some table rows active')
    %for c = tId
    S_surround(tId,:) = [];
    iL = S_surround.idI_surround(1);
    jL = S_surround.idJ_surround(1); 
    i_all = [i_all; iL];
    j_all = [j_all; jL];
    %end
end


% One of these conditions must be met and iL and jL assigned. iL and jL then
% become the next set of active cells.
% Also store the positions of the surrounding cells in  mat
idI_surround = [iL, iL, iL+1, iL+1, iL+1, iL-1, iL-1,iL-1]';
idJ_surround = [jL-1, jL+1, jL-1, jL, jL+1, jL, jL+1, jL-1]';

% 25th May 2023, change from finding the lowest elevation to the most
% downhill gradient
surround_cells = [((mat(jL-1,iL)-mat(jL,iL))/res); ((mat(jL+1,iL)-mat(jL,iL))/res); ((mat(jL-1,iL+1)-mat(jL,iL))/sqrt(2*res^2));((mat(jL,iL+1)-mat(jL,iL))/res);...
    ((mat(jL+1,iL+1)-mat(jL,iL))/sqrt(2*res^2)); ((mat(jL,iL-1)-mat(jL,iL))/res); ((mat(jL+1,iL-1)-mat(jL,iL))/sqrt(2*res^2));  ((mat(jL-1,iL-1)-mat(jL,iL))/sqrt(2*res^2))];

% for plotting create matrix where cell values are the number of steps    
%sprintf('%d', length(i_all))
%nb_steps(jL, iL) = length(i_all);    
 
% stop the simulation when we reach the crater buffer
    if buffmat(jL, iL) == 10000
         i_all = [i_all; iL];
         j_all = [j_all; jL];
        fprintf('%s', 'Buffer reached')
        % storejL = [storejL; jL]; storeiL = [storeiL; iL];
        break
    end


    if jL == size(mat,1)-1
        i_all = [i_all; iL];
        j_all = [j_all; jL];
        break
    end

    if iL == size(mat,2)-1
        break
    end

  


% plot timesteps for every 100 steps
bool = (mod(length(i_all),ts_save) == 0);
timestep_mat = nan(size(mat));

%** added 26 May 2023
% this change means that  when we plot the cells they line up correctly
% with the DEM grid cells
% DEM_xcells_new = DEM_xcells-(res/2);
% DEM_ycells_new = DEM_ycells-(res/2);
% 
% 
xcells_new = xcells-(res/2);
ycells_new = ycells-(res/2);
for m = 1:length(i_all)
   
        nb_steps(j_all(m), i_all(m)) = m;
end


if bool == 1

    % plot the inundated path through the matrix
for m = 1:length(i_all)
        timestep_mat(j_all(m), i_all(m)) = 1;
        nb_steps(j_all(m), i_all(m)) = m;
end
        figure('Visible','off')
        name = sprintf('%s%d%s%d', 'Initialisation point ', coord, '- timestep ', length(i_all));
        path = sprintf('%s/%s/%d%s%s', 'Out', volcano, maxr+1, '/', name);
        imageschs(DEM)
        hold on
        title(sprintf('%s', name))
        %pcolor(dem_xcells, dem_ycells, timestep_mat)
        pcolor(DEM_xcells_new, DEM_ycells_new, timestep_mat)

        shading flat
        xlabel('East')
        ylabel('West')
        scatter(craterX_temp,craterY_temp, 'kx')
        plot(x_all, y_all, 'k')
        colorbar off;
        xlim([min(x_all)-500, max(x_all)+500])
        ylim([min(y_all)-500, max(y_all)+500])
        saveas(gcf,strcat(path, '.png'))

end
end




% plot the inundated path through the matrix
for m = 1:length(i_all)
        new_mat(j_all(m), i_all(m)) = 1;
end 

new_mat_all(:,:,coord)=new_mat;
nb_steps_all(:,:,coord)=nb_steps;

% Added 26th Mary 2023
nb_steps_inv = (1-nb_steps)+max(max(nb_steps));
% invert number of steps (Added 25 May 2023)
nb_steps_inv_all(:,:,coord)=nb_steps_inv;


figure('Visible', 'off')

%%Create two axes
yyaxis left
imageschs(DEM)
colorbar off;
hold on
plot(x_all, y_all, 'k')
xlabel('East')
ylabel('North')
xlim([min(x_all)-500, max(x_all)+500])
ylim([min(y_all)-500, max(y_all)+500])
ax = gca;
ax.YAxis(1).Color = 'k';

yyaxis right
pcolor(DEM_xcells, DEM_ycells, nb_steps)
shading flat
colormap jet
c = colorbar;
c.Label.String = 'Averaged step number';
linkaxes
xlim([min(x_all)-500, max(x_all)+500])
ylim([min(y_all)-500, max(y_all)+500])
yticks([])
ax = gca;
ax.YAxis(1).Color = 'k';

% store the coordinates of the 
if coord == 1
    buff_start_coordX = x_all(round(T.mid)); buff_start_coordY = y_all(round(T.mid));
end
end



 %% Process results for plotting REG

    
  % Calculate the average and standard deviation for bins (stage 1)
    % extract the probability column of each table 
    all_prob = zeros(360/interp_to, length(xcells)); 
    all_elevGain = zeros(360/interp_to, length(xcells)); 
       for i = 1:height(T_all) 
            actT = T_all{i,1};
            act = actT.prob;
            all_prob(:,i) =  act;
            elevGain = actT.interpEC;
            all_elevGain(:,i) = elevGain;
       end
     
    sumT = sum(all_prob,2)/length(xcells);
    
    % calculate SD
    stdev = zeros(1,360/interp_to);
        for i = 1:size(all_prob,1)
            stdev(i) = std(all_prob(i,:)); 
        end
        % convert std into standard error
    SE = stdev/sqrt(length(xcells)); 

    % calculate the average of the elevation gains
    AEG = sum(all_elevGain,2)/length(xcells);
    AEG = table(AEG);

   %Identify elevation change above threshold, use this to set marker size
    AEG.isBelow = AEG.AEG < thr;
    AEG.isAbove = AEG.AEG >= thr;
    AEG.size(AEG.isBelow) = 1;
    AEG.size(AEG.isAbove) = 5;


    % Get coordinates of bin centerpoints along the buffer limit
    % these can be used for running flow models
    Xcoords = x_all(round(T.mid)); Ycoords = y_all(round(T.mid));


%% Process results for plotting LCP
% times inundated
new_mat_all(isnan(new_mat_all))=0;
summed_new_mat_all = sum(new_mat_all,3);
summed_new_mat_all(summed_new_mat_all==0)=nan;

% number of steps
nb_steps_inv_all(isnan(nb_steps_inv_all))=0;

nb_steps_all(isnan(nb_steps_all))=0;
summed_nb_steps_inv_all = sum(nb_steps_inv_all,3);
% summed_nb_steps_all = summed_nb_steps_all/coord;
summed_nb_steps_inv_all(summed_nb_steps_inv_all==0)=nan;

%% Plotting 
% Adjust for plotting
DEM_xcells_new = DEM_xcells-(res/2);
DEM_ycells_new = DEM_ycells-(res/2);

% convert the buffer into gridcells for plotting
str = strel('square',3);
% Make the dilated object
dilated = imdilate(in,str);
border = dilated-in;
border(border==0)=nan;

% Save workspace
save(sprintf('%s/%s/%d/%s', 'Out', volcano, maxr+1, 'workspace'))

% Plot main figure
figure
set(gcf, 'Position', get(0, 'Screensize'));
subplot(2,3,2);
set(gca, 'Color', 'none');
set(gca, 'XColor', 'None')
set(gca, 'YColor', 'None')
rho = (max(sumT)+1)+zeros(height(AEG),1);
colors = AEG.AEG;
sz = (AEG.size)*50;
tbl = table(T.mid*pi/180, rho, colors, sz);
a = axes; a.Position = [0.4022 0.5840 0.1820 0.3145];
a.XColor =  'None';a.YColor = 'None';
set(gca, 'YColor', 'None')
polarscatter(tbl, 'Var1', 'rho', 'filled', 'ColorVariable', 'colors', 'SizeVariable', 'sz', 'Marker', 'diamond')
c = colorbar;
c.Position = [ 0.6101    0.5840    0.0092    0.3400];
colormap parula
c.FontSize = 14;
c.Label.String = ['\fontsize{14} Elevation gain (m)']; 
set(gca, 'Color', 'none');
hold on
edges = [(T.LL*pi/180); ((T.LL(end)+interp_to)*pi/180)]';
polarhistogram('BinEdges',edges,'BinCounts',sumT, 'FaceColor',[0.33,0.09,0.70],'FaceAlpha',.8);
set(gca, 'ThetaDir', 'clockwise', 'ThetaZeroLocation', 'top');
thetaticklabels({'{\bf N}', 'NNE', 'NE', 'ENE', '{\bf E}', 'ESE', 'SE', 'SSE', '{\bf S}',...
    'SSW', 'SW', 'WSW', '{\bf W}', 'WNW', 'NW', 'NNW'})
thetaticks(0:interp_to:swath_nb)
title('Azimuthal elevation difference')
hold on
ang = T.mid.*pi/180;
polarwitherrorbar(ang,sumT,SE') % plot error bars on the data
set(gca, 'Fontsize', 14)

all = {};
rtl = rticklabels;
for r = 1:length(rtl)
    tmp = rtl{r};
    new_rtl = sprintf('%s%s', tmp, '%');
all{r} = new_rtl;
end
hold on
rticklabels(all)
set(gca, 'Color', 'None')

sub_3 = subplot(2,3,3);
pos = sub_3.Position;

ax1 = axes('Position',[pos]);
imageschs(DEM,[],'colormap',[.9 .9 .9],'colorbar',false);
hold on
pcolor(DEM_xcells_new, DEM_ycells_new, border)
shading flat;
cols = [1,1,1;0,0,0];
colormap(gca, cols)
xlim([min(x_all)-500, max(x_all)+500])
ylim([min(y_all)-500, max(y_all)+500])
ax1.XTick = [];
ax1.YTick = [];

ax2 = axes('Position',[pos]);
pcolor(DEM_xcells_new, DEM_ycells_new, summed_nb_steps_inv_all)
linkaxes([ax1,ax2])
xlim([min(x_all)-500, max(x_all)+500])
ylim([min(y_all)-500, max(y_all)+500])
ax2.DataAspectRatio = ax1.DataAspectRatio
set(gca, 'Color', 'None'), set(gca, 'Fontsize', 14)
xlim([min(x_all)-500, max(x_all)+500])
ylim([min(y_all)-500, max(y_all)+500])
ax2.DataAspectRatio = ax1.DataAspectRatio
shading flat
hold on
set(gca, 'Color', 'None'), set(gca, 'Fontsize', 14)
scatter(xcells_new+res/2, ycells_new-res/2, 'rx')%linkaxes([ax1,ax2])
xlabel('Easting')
ylabel('Northing')
title('Least cost path')
set(gca, 'Fontsize', 14)
colormap(ax2,'jet')
cb1 = colorbar;
cb1.Position = [0.91,0.586,0.0092,0.34];
cb1.Label.String = 'Summed inverse propagation step number';
cb1.FontSize = 14;
sub_3.Visible = 'off'
set(gca,'ColorScale','log')

sub_1 = subplot(2,3,1);
imageschs(DEM,[],'colormap',[.9 .9 .9],'colorbar',false);
hold on; 
pcolor(DEM_xcells_new, DEM_ycells_new, border)
shading flat;
cols = [1,1,1;0,0,0];
colormap(gca, cols)
scatter(xcells_new+res/2, ycells_new-res/2, 'rx')
xlabel('Easting')
ylabel('Northing')
t1 = title(sprintf('%s', volcano), 'fontsize', 14);
set(gca, 'Color', 'None'), set(gca, 'Fontsize', 14)
XLim =  [min(x_all)-500, max(x_all)+500];
YLim = [min(y_all)-500, max(y_all)+500];
set(gca, xlim=XLim)
set(gca, ylim=YLim)

subplot(2,3,4:6)
plot((1:360),elev_all, 'k')
hold on
xlim([0, swath_nb])
xlb = xlabel('Direction');
xlb.Position(2) = xlb.Position(2) - 25;
ylabel('Buffer elevation (m)')
set(gca, 'Color', 'None'), set(gca, 'Fontsize', 14);
elevStart = swathAll(1,1);
% relabel x axis to bin limits
labs = {['{\bf N}' newline '0{\circ}'], ['NNE' newline], ['NE' newline], ['ENE' newline], ['{\bf E}' newline '90{\circ}'], ['ESE' newline], ['SE' newline], ['SSE' newline], ['{\bf  S}' newline '180{\circ}'],...
    ['SSW' newline], ['SW' newline], ['WSW' newline], ['{\bf W}' newline '270{\circ}'], ['WNW' newline], ['NW' newline], ['NNW' newline], ['{\bf N}' newline '360{\circ}']};
xticks([0; T.LL]);
xtickloc = ([0; T.mid]);
xticklabels([])
a = zeros(length(labs),1); 
a(:) = (min(yticks))-20; % get y position for labels
% add x bin limit labels
for i = 1:length(labs)
text(xtickloc(i)-2, a(i), labs(i), 'FontSize', 14)
end
title(' Buffer elevation profile','HorizontalAlignment', 'right')
set(gca, 'XGrid', 'on')
yline(elevStart, 'r--')
text(20, double(elevStart+2),'Elevation of starting coordinate', 'color', 'r', 'FontSize',14)
set(gca, 'Color', 'none')
 set(gca, 'Position', [0.13,0.217,...
     0.825,0.261])
 set(gcf, 'Position', get(0, 'Screensize'));
 set(gcf, 'PaperType', 'A1', 'PaperOrientation', 'landscape')


savefig(gcf, sprintf('%s/%s/%d/%s','Out', volcano, maxr+1, volcano))
print(gcf, '-dpdf', fullfile(sprintf('%s/%s/%d/%s','Out', volcano, maxr+1, volcano)))


lab = {'NNE','NE', 'ENE', 'E', 'ESE', 'SE', 'SSE', 'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW', 'N'};
out = table(lab', buff_start_coordX',buff_start_coordY',sumT);
out.Properties.VariableNames = {'Direction', 'X', 'Y', 'AED Probability'}
end