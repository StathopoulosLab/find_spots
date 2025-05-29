function [stat, p, p_ttest, avg, stat_all, p_all, mean_y, err_y, groups,x,y] = plot_in_situ_quantification(data,...
    field, x_order_label, c_order, norm_true, control_cond, triangle_tf, y_limits, control_norm, distribution_tf)
%PLOT_IN_SITU_QUANTIFICATION Plot in situ quantification
% 
%   Inputs
%       data: data structure from quantify_in_situ
%       field: names of the field for averaging and plotting
%
%   Outputs
%       None
% 
%   Overview
%       This function plots the data from quantify_in_situ
    
    if ~iscell(data)
        data = {data};
    end

    if ~iscell(x_order_label)
        x_order_label = {x_order_label};
    end

    if ~iscell(c_order)
        c_order = {c_order};
    end

    if ~iscell(control_cond)
        control_cond = {control_cond};
    end

    avg = cell(size(data,2), 1);
    stat = cell(size(data,2), 1);
    p = cell(size(data,2), 1);
    p_ttest = cell(size(data,2), 1);

    for i = 1:size(data,2)
        if distribution_tf
            pool_geneotypes(data{i}, field);
            stat{i} = [];
            p{i} = [];
            p_ttest{i} = [];
            stat_all = [];
            p_all = [];
            mean_y = [];
            err_y = [];
            groups = [];
        else

            % Find the unique conditions in data
            conditions = unique({data{i}.condition}', 'stable');
            
            % Calulate the mean
            avg{i} = calc_means(data{i}, conditions);
            
            if size(avg{i},2) > 1
                [stat{i}, p{i}, p_ttest{i}] = statistical_analysis(avg{i}, field, false);
            else
                stat{i} = [];
                p{i} = [];
                p_ttest{i} = [];
            end
            
            if ~norm_true
                % Plot the mean for the given field
                [stat_all, p_all, mean_y, err_y, groups] =  plot_mean_intensity(avg{i}, field, x_order_label{i}, c_order{i},...
                    norm_true, control_cond{i}, triangle_tf, y_limits, control_norm);
            end
        end
    end

    if norm_true
        % Plot the mean for the given field
        [stat_all, p_all, mean_y, err_y, groups, x, y] = plot_mean_intensity(avg, field, x_order_label{:}, c_order{:},...
            norm_true, control_cond, triangle_tf, y_limits, control_norm);
    end

%     stat_all = [];
%     p_all = [];
%     mean_y = [];
%     err_y = [];
%     groups = [];
end

function avg = calc_means(data, condition)
%CALC_MEANS Calculate the mean intensity
% 
%   Inputs
%       data: data structure from main function from quantify_in_situ
%       condition: the condition of treatment
% 
%   Outputs
%       avg: a structure containg the average data, the individual data,
%           and the error bar data
% 
%   Overview
%       Calculates the mean and error for data
            
    % Make structure for storing averaged data
    avg = struct('condition', [],...
                 'norm_I_avg', cell(3,size(condition, 1)),...
                 'sum_I_avg', [],...
                 'norm_sum_I_avg', [],...
                 'norm_A_avg', [],...
                 'norm_Maj_avg', [],...
                 'norm_Min_avg', [],...
                 'Maj_em_avg', [],...
                 'Min_em_avg', [],...
                 'A_em_avg', [],...
                 'I_em_avg', [],...
                 'Maj_im_avg', [],...
                 'Min_im_avg', [],...
                 'A_im_avg', [],...
                 'I_im_avg', [],...
                 'A_bg_avg', [],...
                 'I_bg_avg', [],...
                 'varI_im_avg', [],...
                 'disp_ind_im_avg', [],...
                 'norm_MaxFeret_avg', [],...
                 'norm_MinFeret_avg', [],...
                 'MaxFeret_im_avg', [],...
                 'MinFeret_im_avg', [],...
                 'MaxFeret_em_avg', [],...
                 'MinFeret_em_avg', [],...
                 'aspect_r_avg_axis', [],...
                 'Perimeter_em_avg', [],...
                 'Perimeter_im_avg', [],...
                  'width_avg', [],...
                 'length_avg', [],...
                 'aspect_r_avg', [],...
                 'norm_width_avg', [],...
                 'A_over_length_avg', [],...
                 'Perimeter_to_Area_avg',[],... 
                 'Mean_curvature_avg',[],... 
                 'Std_curvature_avg',[]);
             
    % Save field names
    data_fields = fieldnames(avg);
    data_fields = data_fields(2:end);
               
    % For each entered condition
    for i = 1:size(condition, 1)
        % Find indices of data that match entered condition (logical
        % indexing)
        j = strcmp({data.condition}, condition{i,1});
        
        % For each field
        for k = 1:size(data_fields, 1)
            % Save the individual data
            avg(1,i).(data_fields{k}) = cat(1, data(j).(data_fields{k}));
            
            % Calculate the mean
            avg(2,i).(data_fields{k}) = mean(cat(1,...
                                        data(j).(data_fields{k})), "omitnan");
            
            % Calculate error for error bars
            avg(3,i).(data_fields{k}) = calc_error(cat(1, ...
                                        data(j).(data_fields{k})), 'SD');%SD%SEM
        end
        
        % Save the condition
        avg(1,i).condition = repmat(condition(i,1), size(avg(1,i).norm_I_avg));
        avg(2,i).condition = condition{i,1};
        avg(3,i).condition = condition{i,1};
    end
end

function err_d = calc_error(d, select_error)
%CALC_ERROR Calculates the error for data d
% 
%   Input
%       d: data points 
%       select_error: a string, either SEM, CI, or SD
% 
%   Output
%       err_d: the error for the data
% 
%   Overview
%       This function calculates the error for determining error bars. It
%       takes data d and the choice for calculating the error, either
%       standard error of the mean (SEM), 95% confidence intervals (CI), or
%       standard deviation (SD)
    
    % standard deviation for data in d
%     STD_d = nanstd(d, [], 1);
    STD_d = std(d, 0, 1, 'omitnan');

    % standard error of the mean for data in d
    SEM_d = STD_d ./ sqrt(sum(~isnan(d), 1));

    % confidence interval for data in d
    ts_d = tinv(0.975, sum(~isnan(d), 1) - 1);
    CI_d = ts_d .* SEM_d;

    % If user inputed SD
    if ~isempty(select_error) && isequal(select_error, 'SD')
        % Error is standard deviation
        err_d = STD_d;
    % Else if user inputed CI
    elseif ~isempty(select_error) && isequal(select_error, 'CI')
        % Error is confidence intervals
        err_d = CI_d;
    % Else if user inputed SEM or anything else
    else
        % Error is standard error of the mean
        err_d = SEM_d;
    end
end

function [stat, p, mean_y, err_y, unordered_groups, x, y] = plot_mean_intensity(avg, field, x_label_order, c_order,...
    norm_true, control_cond, change_marker, y_limits, control_norm)
%PLOT_MEAN_INTENSITY Plot the individual intensity, mean, and error bars
% 
%   Inputs
%       avg: the avg structure from calc_means
%       field: the field to be plotted
% 
%   Outputs
%       None
% 
%   Overview
%       A plot is made of the individual data, the mean, and the error bars
%       for the data specified by field
            
    % Array of colors
    colors = [
        0.69, 0.55, 0.36;  % 1) Yellow-brown (base)
        0.00, 0.20, 0.40;  % 2) Dark blue (base)
        0.00, 0.35, 0.00;  % 3) Dark green (base)
        
        0.79, 0.63, 0.48;  % 4) Lighter yellow-brown
        0.20, 0.36, 0.55;  % 5) Lighter dark blue
        0.20, 0.50, 0.20;  % 6) Lighter dark green

        %0.3, 0.0, 0.5; % Dark purple
        
        0.86, 0.72, 0.60;  % 7) More light yellow-brown
        0.35, 0.52, 0.70;  % 8) More light dark blue
        0.35, 0.65, 0.35;  % 9) More light dark green
        
        0.7, 0.5, 0.9; % Light purple
        
        0.92, 0.80, 0.72;  % 10) Even lighter yellow-brown
        0.50, 0.66, 0.83;  % 11) Even lighter dark blue
        0.50, 0.78, 0.50;  % 12) Even lighter dark green
        
        0.96, 0.88, 0.84   % 13) Lightest yellow-brown
    ];
               
    % Concatenate the data (individual, mean, error, and condition) for the
    % specified field
    if norm_true
        y = cell(size(avg, 1),1);
        mean_y = cell(size(avg, 1),1);
        err_y = cell(size(avg, 1),1);
        g = cell(size(avg, 1),1);
        control_y = cell(size(avg, 1),1);
        control_ind = cell(size(avg, 1),1);

        for k = 1:size(avg, 1)
            control_y{k} = avg{k}(1,strcmp({avg{k}(2,:).condition}, control_cond{k})).(field)...
                / avg{k}(2,strcmp({avg{k}(2,:).condition}, control_cond{k})).(field);

            y{k} = cat(1, avg{k}(1,:).(field)) / avg{k}(2,strcmp({avg{k}(2,:).condition}, control_cond{k})).(field);
%             mean_y{k} = cat(1, avg{k}(2,:).(field)) / avg{k}(2,strcmp({avg{k}(2,:).condition}, control_cond{k})).(field);
%             err_y{k} = cat(1, avg{k}(3,:).(field)) / avg{k}(2,strcmp({avg{k}(2,:).condition}, control_cond{k})).(field);
            g{k} = cat(1, avg{k}(1,:).condition);
            control_ind{k} = strcmp({avg{k}(2,:).condition}, control_cond{k});
        end

%         control_y = cat(1, control_y{:});
        y = cat(1, y{:});% + mean(control_y);
%         mean_y = cat(1, mean_y{:});% + mean(control_y);
%         err_y = cat(1, err_y{:});
        g = cat(1, g{:});

%         control_ind = cat(2, control_ind{:});

%         ind_loc = find(control_ind);
%         err_y(ind_loc(1)) = calc_error(control_y, 'SD');

%         for m = size(ind_loc,2):-1:2
%             mean_y(ind_loc(m)) = [];
%             err_y(ind_loc(m)) = [];
%         end
    else
        if iscell(avg)
            y = cell(size(avg, 1),1);
            g = cell(size(avg, 1),1);
    
            for k = 1:size(avg, 1)
                y{k} = cat(1, avg{k}(1,:).(field));
                g{k} = cat(1, avg{k}(1,:).condition);
            end

            y = cat(1, y{:});
            g = cat(1, g{:});
        else
            y = cat(1, avg(1,:).(field));
            mean_y = cat(1, avg(2,:).(field));
            err_y = cat(1, avg(3,:).(field));
            g = cat(1, avg(1,:).condition);
        end
    end
    
    % Find the unique conditions and initialize variables
    unordered_groups = unique(g, 'stable');
    groups = unordered_groups(x_label_order);
    x = zeros(size(g,1), 1);
    c = zeros(size(g,1), 3);
    mean_x = zeros(size(groups,1), 1);

    if norm_true || iscell(avg)
        mean_y = zeros(size(groups,1), 1);
        err_y = zeros(size(groups,1), 1);
    end

    % For each condition
    for i = 1:size(groups, 1)
        % Create logical array where condition matches
        ind = strcmp(g, groups{i});
        mean_ind = strcmp(unordered_groups, groups{i});

        if norm_true || iscell(avg)
            % Calculate the mean
            mean_y(mean_ind) = mean(y(strcmp(g, groups{i})), "omitnan");
            
            % Calculate error for error bars
            err_y(mean_ind) = calc_error(y(strcmp(g, groups{i})), 'SD');%SD%SEM
        end
        
        % Save i for only the matched conditions to plot all points with
        % the same condition at the same x
        x(ind) = i;
        mean_x(mean_ind) = i;
        
        % Assign a color to each point. Color is picked by using mod in
        % case a color needs to be repeated. The loop saves each column of
        % colors
        for j = 1:size(colors,2)
            c(ind,j) = colors(mod(c_order(i)-1, size(colors,1))+1,j);
%             c(ind,j) = colors(8,j);
        end
    end

%     if any(strcmp(groups, '40'))
%         data_40 = y(strcmp(g, '40'));
%         data_YW = y(strcmp(g, 'YW'));
%         
%         combined_data = cat(1, data_YW, data_40);
% 
%         mean_y(strcmp(unordered_groups, '40')) = mean(combined_data);
%         mean_y(strcmp(unordered_groups, 'YW')) = mean(combined_data);
% 
%         err_y(strcmp(unordered_groups, '40')) = calc_error(combined_data, 'SEM');
%         err_y(strcmp(unordered_groups, 'YW')) = calc_error(combined_data, 'SEM');
% 
%         groups(strcmp(groups, '40')) = [];
%     end
    if size(groups,1) == 2
        condition1 = y(strcmp(g,groups{1}));
        condition2 = y(strcmp(g,groups{2}));
        % Initialize variables for making comparison tables
        p = cell(2,2);

        % Save time point i in table of mutiple comparisons
        p{1, 1} = 'p-values';
    
        % Make row names of conditions for comparison
        p{2, 1} = groups{1};
    
        % Make column names of conditions for comparison
        p{1, 2} = groups{2};
            
        [~, p{2,2}] = ttest2(condition1, condition2, 'Vartype', 'unequal');
        stat = [];
    else
        [stat, p] = statistical_analysis_all(y, g);
    end
    
    % Make a figure and keep the axis for plotting the raw data, the mean,
    % and the error bars on the same plot
    figure;
    hold on
    plot([0, size(groups,1)+1], [mean_y(strcmp(unordered_groups, control_norm)),...
        mean_y(strcmp(unordered_groups, control_norm))], '--', 'Color', 'k', 'LineWidth', 2);
    
    if change_marker
        for j = 1:size(groups, 1)
            if any(j == (1:2:size(groups, 1)))
                % Plot raw data with jitter to offset the points with some transparency
                scatter(x(x==j), y(x==j), 100, c(x==j,:), 'filled', 'jitter', 'on', 'jitteramount', 0.2,...
                        'MarkerFaceAlpha', .5,'MarkerEdgeAlpha', .5);
            else
                % Plot raw data with jitter to offset the points with some transparency
                scatter(x(x==j), y(x==j), 100, c(x==j,:), '^', 'filled', 'jitter', 'on', 'jitteramount', 0.2,...
                        'MarkerFaceAlpha', .5,'MarkerEdgeAlpha', .5);
            end
        end
    else
        % Plot raw data with jitter to offset the points with some transparency
        scatter(x, y, 100, c, 'filled', 'jitter', 'on', 'jitteramount', 0.2,...
                'MarkerFaceAlpha', .5,'MarkerEdgeAlpha', .5);
    end
    
    % Plot the mean with the error bars and set properties
    h = errorbar(mean_x, mean_y, err_y, '.', 'Color', 'k');
    set(h, 'linewidth', 2, 'markersize', 25);

    hold off

    set(gca,'fontname','arial');
%     set(gca,'YScale','log');
    
    if isempty(y_limits)
        y_limits = [0.95 .* min(y), 1.05 .* max(y)];
    end

    % Set properties of axis
    set(gca, 'xlim', [0.5, size(groups,1)+0.5],...
             'xtick', 1:size(groups,1), ...
             'xticklabels', groups,...
             'XTickLabelRotation', 45,...
             'ylim', y_limits,...%[0.02,4] [-0.1,3] [40, 200] [0, 10000] [-3500, 7000]
             'fontsize', 20);  
end

function [stat, p, p_ttest] = statistical_analysis(avg, field, indiv_ttest)
%STATISTICAL_ANALYSIS Perform ANOVA to compare the means between conditions
% 
%   Input
%       avg: the structure returned from calc_means
% 
%   Output
%       stat: structure containing outputs from anova1 and multcompare
%       p: table of p-values for pairwise comparisons
% 
%   Overview
%       This function performs statistical analysis on the data.
%       Specifically, it performs one way ANOVA using anova1 and multiple
%       comparisons using Tukey's HSD using multcompare. It returns the
%       outputs from anova1 and multcompare in the structure stat and
%       a table of p-values, p, for pairwise comparison between conditions.
    
    % To calculate individual t tests between groups of two samples,
    % organize samples so samples to be tested are concatanated together
    % (for example column 1 and 2 will be tested, 3 and 4, etc)
    if indiv_ttest
        p_ttest = cell(2, size(avg,2)/2);
        ind = 1;
        
        for i = 1:2:size(avg,2)
            p_ttest{1,ind} = sprintf('%s & %s', avg(2,i).condition, avg(2,i+1).condition);
            [~, p_ttest{2,ind}] = ttest2(avg(1,i).(field), avg(1,i+1).(field), 'Vartype', 'unequal');
            ind = ind + 1;
        end
    else
        p_ttest = [];
    end

    condition = cat(1, avg(1,:).condition);
    data = cat(1, avg(1,:).(field));
    
    % Initialize a structure for storing the results of the statistical
    % analysis
    stat = struct('p', [],...
                  'tbl', [],...
                  'stats', [],...
                  'p_indiv', [],...
                  'means', [],... 
                  'names', []);
    
    % Perform ANOVA on the intensity data grouped by condition
    [stat.p, stat.tbl, stat.stats, stat.p_indiv, stat.means,...
        stat.names] = stat_test(data, condition);
    
    % Initialize variables for making comparison tables
    p = cell(size(stat.names, 1), size(stat.names, 1));

    % Save time point i in table of mutiple comparisons
    p{1, 1} = 'p-values';
    
    % Make row names of conditions for comparison
    p(2:end, 1) = stat.names(1:(end-1));
    
    % Make column names of conditions for comparison
    p(1, 2:end) = stat.names(2:end);
            
    % For each comparison
    for j = 1:size(stat.p_indiv, 1)
        % save the p-value in the p-value table
        p{stat.p_indiv(j,1) + 1,...
            stat.p_indiv(j,2)} = stat.p_indiv(j,6);
    end
end

function [stat, p] = statistical_analysis_all(y, g)
%STATISTICAL_ANALYSIS Perform ANOVA to compare the means between conditions
% 
%   Input
%       avg: the structure returned from calc_means
% 
%   Output
%       stat: structure containing outputs from anova1 and multcompare
%       p: table of p-values for pairwise comparisons
% 
%   Overview
%       This function performs statistical analysis on the data.
%       Specifically, it performs one way ANOVA using anova1 and multiple
%       comparisons using Tukey's HSD using multcompare. It returns the
%       outputs from anova1 and multcompare in the structure stat and
%       a table of p-values, p, for pairwise comparison between conditions.
    
    condition = g;
    data = y;
    
    % Initialize a structure for storing the results of the statistical
    % analysis
    stat = struct('p', [],...
                  'tbl', [],...
                  'stats', [],...
                  'p_indiv', [],...
                  'means', [],... 
                  'names', []);
    
    % Perform ANOVA on the intensity data grouped by condition
    [stat.p, stat.tbl, stat.stats, stat.p_indiv, stat.means,...
        stat.names] = stat_test(data, condition);
    
    % Initialize variables for making comparison tables
    p = cell(size(stat.names, 1), size(stat.names, 1));

    % Save time point i in table of mutiple comparisons
    p{1, 1} = 'p-values';
    
    % Make row names of conditions for comparison
    p(2:end, 1) = stat.names(1:(end-1));
    
    % Make column names of conditions for comparison
    p(1, 2:end) = stat.names(2:end);
            
    % For each comparison
    for j = 1:size(stat.p_indiv, 1)
        % save the p-value in the p-value table
        p{stat.p_indiv(j,1) + 1,...
            stat.p_indiv(j,2)} = stat.p_indiv(j,6);
    end
end

function [p, tbl, stats, p_indiv, means, names] = stat_test(data,...
    group)
%STAT_TEST Perform ANOVA to compare the means between conditions
% 
%   Input
%       data: data that anova will be performed on
%       group: identifier for data to correctly group it
% 
%   Output
%       p: p-value from the anova
%       tbl: a table returned from anova
%       stats: statistics for mutiple comparison tests
%       p_indiv: pairwise p-values from mutiple comparisons
%       means: estimated means
%       names: names of groups
% 
%   Overview
%       This function performs statistical analysis on the data. 
%       Specifically, it performs one way ANOVA using anova1 and multiple
%       comparisons using Tukey's HSD using multcompare. It returns the
%       outputs from anova1 and multcompare in the structure stat.

    % Perform ANOVA on the data grouped by condition in group
    [p, tbl, stats] = anova1(data, group, 'off');
    
    % Perform pairwise comparisons of data between conditions
    % using Tukey's HSD
    [p_indiv, means, ~, names] = multcompare(stats, 'display', 'off');
end

function pool_geneotypes(data, fieldname)
%NORMALIZE_MEAN Subtract background levels from signal levels.
% 
%   Input
%       data: the data structure in the main function
% 
%   Output
%       data: the data structure from the main function that has been
%             updated with normalized data
% 
%   Overview
%       This function takes the data structure from the main function and
%       normalizes the data. Specifically, this function subtracts out the
%       background signal for maximum and sum projections. In addition, the
%       length, width, and area of the signal is normalized by the length,
%       width, or area of the entire embryo.
    
    % % Initialize array
    % genotypes = cell(size(data,2), 1);
    % 
    % % For each data entry
    % for i = 1:size(data,2)
    %     % Split condition string by underscore
    %     condition_split = strsplit(data(i).condition, {'_'});
    % 
    %     % Save the second part of the string, which should be genotype
    %     genotypes{i} = condition_split{2};
    % end

    % % Get unique genotypes
    % unique_genotype = unique(genotypes, 'stable');
    % 
    % % Initialize array
    % pooled_data = struct('condition', cell(size(unique_genotype, 1), 1),...
    %                      'measurements', []);
    % 
    % % For each unique genotype
    % for i = 1:size(unique_genotype, 1)
    %     j = strcmp(genotypes, unique_genotype{i,1});
    % 
    %     pooled_data(i).condition = unique_genotype{i,1};
    %     pooled_data(i).measurements = cat(1,data(j).(fieldname));
    % end

    % figure;
    % for i = 1:2
    %     % Sample data: Replace with your measured distances
    %     distances = pooled_data(i).measurements; % Example: Normally distributed distances
    % 
    %     % % Define histogram bins
    %     % num_bins = 30; 
    %     % 
    %     % % Compute histogram
    %     % [counts, bin_edges] = histcounts(distances, num_bins, 'Normalization', 'pdf');
    %     % 
    %     % % Compute bin centers
    %     % bin_centers = (bin_edges(1:end-1) + bin_edges(2:end)) / 2;
    %     % 
    %     % % Plot PDF
    %     % hold on;
    %     % bar(bin_centers, counts);
    %     % xlabel('Distance');
    %     % ylabel('Probability Density');
    %     % title('Histogram-Based PDF');
    %     % grid on;
    % 
    %     % Generate probability density function (PDF) using ksdensity
    %     [pdf_values, x_pdf] = ksdensity(distances);
    % 
    %     % Plot the PDF
    %     hold  on;
    %     plot(x_pdf, pdf_values, 'LineWidth', 2);
    %     xlabel('Distance');
    %     ylabel('Probability Density');
    %     title('Probability Density Function (PDF)');
    %     grid on;
    %     hold off;
    % end
    % legend({pooled_data.condition});

    % Get unique conditions
    unique_time_genotype = unique({data.condition}, 'stable');

    % Initialize array
    distribution_data = struct('condition', cell(size(unique_time_genotype, 2), 1),...
                         'measurements', []);

    % figure;

    % For each unique genotype
    for i = 1:size(unique_time_genotype, 2)
        j = strcmp({data.condition}, unique_time_genotype{1,i});
        subset_data = data(j);

        distribution_data(i).condition = unique_time_genotype{1,i};
        %distribution_data(i).measurements = cat(1,data(j).(fieldname));
        
        num_embryos = sum(j,2);
        x_range = linspace(0, 140, 500); % Define common x-axis range

        % Initialize PDF storage
        pdf_values = zeros(num_embryos, length(x_range));
        
        figure; hold on; 
        plot_handles = gobjects(num_embryos,1); % Store plot handles
        embryo_names = strings(1, num_embryos); % Store embryo names
        

        % Compute KDE for each embryo and normalize contribution
        for k = 1:num_embryos
            [pdf_k, x_pdf] = ksdensity(subset_data(k).(fieldname), x_range); % Compute KDE for embryo i
            pdf_values(k, :) = pdf_k / trapz(x_pdf, pdf_k); % Normalize area to 1
            % Plot the final normalized PDF
            plot_handles(k) = plot(x_range, pdf_k, 'LineWidth', 2,'DisplayName', subset_data(k).name);
            embryo_names(k) = subset_data(k).name;
        end

        xlabel('Width (pixels or microns)');
        ylabel('Probability Density');
        title('Final Normalized PDF of Widths for the Phenotype');
        grid on;

        % Create an interactive legend
        lgd = legend(plot_handles, embryo_names, 'Interpreter', 'none');
        
        % Add a callback function to toggle visibility
        make_legend_toggle(lgd, plot_handles);
        
        % % Compute the averaged PDF across embryos
        % final_pdf = mean(pdf_values, 1); % Average the individual PDFs
        % 
        % % Normalize the final PDF so that its area sums to 1
        % final_pdf = final_pdf / trapz(x_range, final_pdf); 
        
        % % Plot the final normalized PDF
        % hold on
        % plot(x_range, final_pdf, 'LineWidth', 2);
        % xlabel('Width (pixels or microns)');
        % ylabel('Probability Density');
        % title('Final Normalized PDF of Widths for the Phenotype');
        % grid on;
        % hold off;
    end

    % figure;
    % for i = 1:size(unique_time_genotype, 2)
    % 
    %     % Sample data: Replace with your measured distances
    %     distances = distribution_data(i).measurements; % Example: Normally distributed distances
    % 
    %     % % Define histogram bins
    %     % num_bins = 30; 
    %     % 
    %     % % Compute histogram
    %     % [counts, bin_edges] = histcounts(distances, num_bins, 'Normalization', 'pdf');
    %     % 
    %     % % Compute bin centers
    %     % bin_centers = (bin_edges(1:end-1) + bin_edges(2:end)) / 2;
    %     % 
    %     % % Plot PDF
    %     % hold on;
    %     % bar(bin_centers, counts);
    %     % xlabel('Distance');
    %     % ylabel('Probability Density');
    %     % title('Histogram-Based PDF');
    %     % grid on;
    % 
    %     % % Generate probability density function (PDF) using ksdensity
    %     % [pdf_values, x_pdf] = ksdensity(distances);
    %     % 
    %     % % Plot the PDF
    %     % hold  on;
    %     % plot(x_pdf, pdf_values, 'LineWidth', 2);
    %     % xlabel('Distance');
    %     % ylabel('Probability Density');
    %     % title('Probability Density Function (PDF)');
    %     % grid on;
    %     % hold off;
    % end
    % legend({distribution_data.condition});    
end

% Function to make legend items clickable
function make_legend_toggle(lgd, plot_handles)
    % Find legend text elements
    legend_items = findobj(lgd.PlotChildren, 'Type', 'Line');

    % Ensure we have valid handles
    if length(legend_items) ~= length(plot_handles)
        return;
    end

    % Add a callback function to each legend entry
    for i = 1:length(plot_handles)
        legend_items(i).ButtonDownFcn = @(~, ~) toggle_visibility(plot_handles(i));
    end
end

% Helper function to toggle plot visibility (using transparency)
function toggle_visibility(plot_handle)
    if plot_handle.UserData == 1 % If visible
        plot_handle.Color(4) = 0.2;  % Set transparency (Alpha = 0.5)
        plot_handle.UserData = 0;   % Mark as hidden
    else
        plot_handle.Color(4) = 1;  % Restore full visibility
        plot_handle.UserData = 1;   % Mark as visible
    end
end