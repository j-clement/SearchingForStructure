# File from April 2015

## Importing relevant modules
import numpy as np
import xlwt
import datetime
from time import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

### Defining the storage procedures (excel, PDF, and intermediate storage)

# Giving a name to each file (i.e. each combination of A and omega)
def name_this_file():
    # If shocks are set by the modeler, this creates a list of shock period for the filename:
    shock_period_string = ''        
    for i in shock_periods:
        shock_period_string += str(i)
        if i != np.max(shock_periods):
            shock_period_string += '_'
    # This gives the name
    filename = str('matrix ' + \
        ' runs_' + str(RUNS) + \
        ' M_' + str(M) + \
        ' ' + 'a_' + str(aspiration) + \
        ' o_' + str(omega) + \
        ' s'*shocks + ('p'+str(avg_shock))*shocks*(1-shock_type) + ('t'+shock_period_string)*shocks*shock_type + \
        '_ad'*designer_adapt + \
        ' cbeta'*continuous_beta + ' fbeta'*(1-continuous_beta) + str(np.max(beta_levels)) + \
        ' ' + date)
    return filename

# At the end of each sub-run (i.e. each combination of A, omega, beta, w), append data to the 'GLOBAL' arrays
def append_to_global_storage():
    avg_perf_output = np.round(np.average(PERF_GLOBAL, axis=0),3) # We use this for the graphs
    avg_omm_output = np.round(np.average(OMM_GLOBAL, axis=0),3)
    avg_comm_output = np.round(np.average(COMM_GLOBAL, axis=0),3)
    avg_churn_output = np.round(np.average(CHURN_GLOBAL, axis=0),3)  
    avg_conv_r_d = np.round(np.average(CONV_GLOBAL, axis=0),3)
    avg_asp_status = np.round(np.average(ASP_STATUS_GLOBAL, axis=0),3)
    perf_t_by_t[w_index, beta_index] = avg_perf_output
    GLOBAL_STORAGE_PERF[aspiration_index,omega_index,w_index,beta_index] = avg_perf_output[T]
    GLOBAL_STORAGE_CUMUL[aspiration_index,omega_index,w_index,beta_index] = np.sum(avg_perf_output)
    GLOBAL_STORAGE_CONV[aspiration_index,omega_index,w_index,beta_index] = avg_conv_r_d[T]
    GLOBAL_STORAGE_OMM[aspiration_index,omega_index,w_index,beta_index] = avg_omm_output[T]
    GLOBAL_STORAGE_COMM[aspiration_index,omega_index,w_index,beta_index] = avg_comm_output[T]
    GLOBAL_STORAGE_CHURN[aspiration_index,omega_index,w_index,beta_index] = avg_churn_output[T]
    GLOBAL_STORAGE_ASP[aspiration_index,omega_index,w_index,beta_index] = np.round(np.average(avg_asp_status),3) # This is a global average
                
# Excel
def new_excel_table(variable, title, excelfile):
    sheet = excelfile.add_sheet(title)
    for w_index in range(len(w_levels)):
        w = w_levels[w_index]
        sheet.write(0,w_index+1,str(w))
    for beta_index in range(len(beta_levels)):
        beta = beta_levels[beta_index]
        sheet.write(beta_index+1,0,str(beta))
    for w_index in range(len(w_levels)):
        for beta_index in range(len(beta_levels)):
            sheet.write(beta_index+1, w_index+1, variable[aspiration_index,omega_index,w_index,beta_index])
    
def store_excel():
    book = xlwt.Workbook()
    new_excel_table(GLOBAL_STORAGE_PERF,'Results_top_perf',book)
    new_excel_table(GLOBAL_STORAGE_CUMUL,'Results_cumul_perf',book)
    new_excel_table(GLOBAL_STORAGE_CONV,'Convergence R-D',book)
    new_excel_table(GLOBAL_STORAGE_OMM,'Omission',book)
    new_excel_table(GLOBAL_STORAGE_COMM,'Commission',book)
    new_excel_table(GLOBAL_STORAGE_ASP,'Time above aspirations',book)
    new_excel_table(GLOBAL_STORAGE_CHURN,'Churn',book)
    sheet = book.add_sheet('Index')
    sheet.col(0).width = 10000
    sheet.write(0,0,"COLUMNS represent different values of:")
    sheet.write(1,0,"ROWS represent different values of:")
    sheet.write(0,1,"w")
    sheet.write(1,1,"beta")
    book.save(str(folder + filename + '.xls'))

# PDF
plt.style.use('ggplot') # Setting the plotting style

def global_plot(variable, title, axe, fontsize=12): # Plots at t = T
    x = w_levels # The x values will always be the same (i.e. values of w)
    y1 = variable[aspiration_index, omega_index][:,0] # Line for beta = 0
    y2 = variable[aspiration_index, omega_index][:,1] # Line for beta = the other value specified
    axe.plot(x, y1, color='red', label=r'$\beta =$' + str(beta_levels[0]))
    axe.plot(x, y2, color = 'green', label=r'$\beta =$' + str(beta_levels[1]))
    ymin = np.min((np.min(y1),np.min(y2)))
    ymax = np.max((np.max(y1),np.max(y2)))
    axe.set(ylim = (ymin -0.05*(ymax-ymin), ymax +0.05*(ymax-ymin)))
    axe.locator_params(nbins=len(w_levels))
    axe.set_xlabel('w', fontsize=fontsize)
    #ax.set_ylabel('y-label', fontsize=fontsize)
    axe.set_title(title, fontsize=fontsize, fontweight="bold")

def t_by_t_plot(x, y1, y2, title, axe, fontsize=12): # Plots period by period
    axe.plot(x, y1, color='red', label=r'$\beta =$' + str(beta_levels[0]))
    axe.plot(x, y2, color = 'green', label=r'$\beta =$' + str(beta_levels[1]))
    ymin = np.min((np.min(y1),np.min(y2)))
    ymax = np.max((np.max(y1),np.max(y2)))
    axe.set(ylim = (ymin -0.05*(ymax-ymin), ymax +0.05*(ymax-ymin)))
    if shocks ==1 and shock_type ==1:
        for i in range(len(shock_periods)):
            if i == 0:
                plt.axvline(x=shock_periods[i], linewidth=1, color='yellow', label='shock')
            else: # label only once
                plt.axvline(x=shock_periods[i], linewidth=1, color='yellow')
    axe.locator_params(nbins=len(w_levels))
    axe.set_xlabel('t', fontsize=fontsize)
    #axe.set_ylabel('y-label', fontsize=fontsize)
    axe.set_title(title, fontsize=fontsize, fontweight="bold")
    
def store_pdf():
    pp = PdfPages(str(folder + filename + '.pdf'))
    # FIGURE 1: RESULTS AT t=T
    # Defining the figure for global plots and its shape        
    fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
    ax1 = plt.subplot2grid((5,4),(0,0), colspan = 3)
    ax2 = plt.subplot2grid((5,4),(1,0), colspan = 3)
    ax3 = plt.subplot2grid((5,4),(2,0), colspan = 3)
    ax4 = plt.subplot2grid((5,4),(3,0), colspan = 2)
    ax5 = plt.subplot2grid((5,4),(3,2), colspan = 2)
    ax6 = plt.subplot2grid((5,4),(4,0), colspan = 2)
    ax7 = plt.subplot2grid((5,4),(4,2), colspan = 2)
    # Creating the  global plots
    global_plot(GLOBAL_STORAGE_PERF, 'Average performance at t=T', ax1)
    global_plot(GLOBAL_STORAGE_CUMUL, 'Cumulative performance at t=T', ax2)
    global_plot(GLOBAL_STORAGE_CONV, 'Convergence between R and D at t=T', ax3)
    global_plot(GLOBAL_STORAGE_OMM, 'Omission errors at t=T', ax4)
    global_plot(GLOBAL_STORAGE_COMM, 'Commission errors at t=T', ax5)
    global_plot(GLOBAL_STORAGE_ASP, '% Time spent above aspirations' , ax6)
    global_plot(GLOBAL_STORAGE_CHURN, 'Average churn over all periods', ax7)
    # Adjust the layout and close
    ax3.legend(bbox_to_anchor=(1.05, 1), loc=0, borderaxespad=0.)
    plt.tight_layout()
    fig.text(0.76,0.65, 'M='+str(M) + \
        '\nT='+str(T) + \
        '\nNb of runs='+str(RUNS) + \
        '\n\nA='+str(aspiration) + \
        '\n$\Omega =$'+str(omega) + \
        (1-continuous_beta)*('\nFixed '+r'$\beta$'+'='+str(np.max(beta_levels)))+ \
        continuous_beta*('\nContinuous '+r'$\beta$'+', max='+str(np.max(beta_levels)))+ \
        '\n\n' + \
        (1-shocks)*'No shocks' + shocks*'Shocks are included' + \
        shocks*(1-shock_type)*('\nprobabilistically, avg ='+str(avg_shock)) + \
        shocks*shock_type*('\nin periods '+str(shock_periods)) + \
        shocks*(1-designer_adapt)*"\nDesigner doesn't adapt" + \
        shocks*designer_adapt*'\nDesigner adapts' + \
        '\n\nDensity of E=' + str(E_density) + \
        '\n% reciprocity in E=' + str(p_recip) + \
        '\n\nOmission(weight)=' + str(omm) + \
        '\nCommission(weight)=' + str(comm) \
        , fontsize = 12) 
    pp.savefig(fig) # Save the figure to PDF
    # NEXT FIGURES: PERIOD BY PERIOD AVERAGE PERFORMANCE
    x = np.linspace(0, T, num=T+1)
    for i in range(int(np.ceil(len(w_levels)/6))): 
        fig = plt.figure(figsize=(8.27, 11.69), dpi=100)
        for j in range(np.min((len(w_levels)-i*6, 6))): # maximum of 6 per page
            y1 = perf_t_by_t[j+i*6,0]
            y2 = perf_t_by_t[j+i*6,1]
            ax = plt.subplot2grid((6,5),(j,1), colspan = 3)
            t_by_t_plot(x, y1, y2, 'Perf over time for w=' + str(w_levels[j+i*6]), ax, fontsize=12)
            if j == 0:
                ax.legend(bbox_to_anchor=(1.05, 1), loc=0, borderaxespad=0.)
        plt.tight_layout()
        pp.savefig(fig)
    # End of all figures: close the PDF file
    pp.close()


### Defining important matrix operations


# Alternative algorithm for random network generation, slower but always gives the same density

def new_random_network(density): # This neturns a random network of the given density
    network = np.zeros((M,M))
    flipped_cells = np.random.choice(int(M*(M-1)/2),int(np.round((density)*M*(M-1)/2)), replace=False)
    bottom_half = np.zeros(M) # this is a vector which computes the cumulative number of cells available at each row in the matrix's bottom half
    for i in range(M):
        bottom_half[i] = (i+1)*i/2
        #PP: can use "memoization" and make this array once at top where M is defined
    for k in range(len(flipped_cells)):
        pos = flipped_cells[k] # position of the cell to flip
        row = np.min(np.argwhere((bottom_half >= pos+1)))
        col = int(np.min(np.argwhere((bottom_half >= pos+1)))-(bottom_half[np.min(np.argwhere((bottom_half >= pos+1)))]-pos))
        # This flips the randomly chosen cells in the bottom half of the matrix:
        network[row][col] = 1
        # PP:CAUTION: col is float,row is int
        #PP: CAN MAKE "DENSITY PRESERVING RANDOM FLIPS" A SEPARATE FUNCTION LINES 183-188
    network = np.trunc(network + np.transpose(network))
    np.fill_diagonal(network,1)
    return network

'''
# This algorithm for random network generation is fast but never gives the exact same density
def new_random_network(density): # This neturns a random network of the given density
    networkx_matrix = nx.fast_gnp_random_graph(M, density, seed=None, directed=False)
    numpy_matrix = nx.to_numpy_matrix(networkx_matrix) # convert from NetworkX to Numpy
    numpy_array=np.array(numpy_matrix)
    np.fill_diagonal(numpy_array,1)
    return numpy_array
'''

def generate_new_task_structure():
    new_E_matrix = new_random_network(density=E_density)
    # Introducing sequential interdependences
    # (by flipping cells for only half of the matrix)
    bottom_half = np.zeros(M) # this is a vector which computes the cumulative number of cells available at each row in the matrix's bottom half
    for i in range(M):
        bottom_half[i] = (i+1)*i/2
    flipped_cells = np.random.choice(int(M*(M-1)/2),int(np.round((1-p_recip)*M*(M-1)/2)), replace=False)
    for k in range(len(flipped_cells)):
        pos = flipped_cells[k] # position of the cell to flip
        row = np.min(np.argwhere((bottom_half >= pos+1)))
        col = int(np.min(np.argwhere((bottom_half >= pos+1)))-(bottom_half[np.min(np.argwhere((bottom_half >= pos+1)))]-pos))
        # This flips the randomly chosen cells in the bottom half of the matrix:
        if new_E_matrix[row][col] == 1:
            new_E_matrix[row][col] = 0
        elif new_E_matrix[row][col] == 0:
            new_E_matrix[row][col] = 1
        else:
            print("PROBLEM\a")
    return new_E_matrix

def designer_adapts_to(task_structure):
    distance_matrix = np.copy(task_structure)
    # Introducing the designer's accuracy
    # (by flipping cells for the entire matrix)
    flipped_cells = np.random.choice(int(M*(M-1)),int(np.round((1-omega)*M*(M-1))), replace=False)
    for k in range(len(flipped_cells)):
        pos = flipped_cells[k]
        row = pos//(M-1)
        diagonal = 0
        if pos % (M-1) >= row: # This avoids the diagonal in order to flip the cell in the right column
            diagonal = 1
        col = pos%(M-1) + diagonal
        # This flips the randomly chosen cells, avoiding the diagonal
        if distance_matrix[row][col] == 1:
            distance_matrix[row][col] = 0
        elif distance_matrix[row][col] == 0:
            distance_matrix[row][col] = 1
        else:
            print("PROBLEM\a")
    D_undirected = (distance_matrix + np.transpose(distance_matrix))/2
    # Here, I am assuming that the designer puts two agents together in the formal structure when the cost of ommission is greater or equal than
    # the cost of commission
    if omm >= comm:
        D_undirected[D_undirected == 0.5] = 1
    elif omm < comm:
        D_undirected[D_undirected == 0.5] = 0
    else:
        print("PROBLEM\a")
    distance_matrix = np.copy(D_undirected)
    return distance_matrix

def agents_determine_attractiveness(new_D, past_R):
    F_attractiveness = w*new_D + (1-w)*past_R # The initial attractiveness function is random, not determined by any parameter
    #F_before_inertia = np.zeros((T+1,M,M)) # This will be used in the iterations, when we need to take alpha into account
    F_random = np.round(np.random.rand(M,M),3)
    newF = F_attractiveness - F_random[0]
    newF[newF>=0]=1 # This updates F accordingly
    newF[newF<0]=0
    newR = np.trunc((newF + np.transpose(newF))/2) # Computes R as a two-sided match of F
    return (newF, newR)

def performance_of_agents(past_R, task_structure):
    deductions = np.array(task_structure - past_R) # Matrix of all deductions from the ideal performance score
    nb_omm = (deductions ==1).sum() # counts the number of omission errors
    nb_comm = (deductions ==-1).sum() # counts the number of comission errors
    # Back to the measurement of performance
    deductions[deductions==1] = omm # deductions for errors of ommission...
    deductions[deductions==-1] = comm # ... and commission
    deductions_sum = np.sum(deductions, axis=1) # Performance is obtained by summing up deductions...
    new_P = np.array(((M-1)-deductions_sum)/(M-1)) # ... and dividing them by the maximum performance score
    #PP: can introduce a) ruggedness via diffrential weights on getting differnt edges right b) via noise and c)80:20 rule-concave increasing function 
    return (new_P, nb_omm, nb_comm) # returns performance, omission and commission errors.
    
def agent_explores(initial_F, aspirations, performance):
    if continuous_beta == 0:
        beta_actual = beta
    elif continuous_beta == 1:
        beta_actual = beta*(aspirations-performance)/aspirations
    # Flipping cells of F randomly with probability 'beta'
    flipped_cells = np.random.choice(M-1,int(np.round(beta_actual*(M-1))), replace=False) # This chooses beta*M cells at random
    for k in range(len(flipped_cells)):
        pos = flipped_cells[k]
        diagonal = 0
        if pos >= m: # This avoids the diagonal in order to flip the cell in the right column
            diagonal = 1
        col = pos + diagonal
        # This flips the randomly chosen cells
        if initial_F[col] == 1:
            initial_F[col] = 0
        elif initial_F[col] == 0:
            initial_F[col] = 1
        else:
            print("PROBLEM\a")


date = str(datetime.date.today()) # Add the date to the file name
start = time()  # this option starts the clock    

# Folder where exports will be saved
folder = r'C://Users//JC944//Downloads//'

### GENERAL PARAMETERS OF THE MODEL

## Number of runs
RUNS = 100

## Number of agents
M = 15
## Number of periods
T =  300

'''Below, I use the "linspace" function to run the model for different values 
of the parameters in a certain range. However, because the model takes a long 
time to run, I typically run it for one value of aspiration and one value of 
omega at a time. This is why the two first parameters look like 
"np.linspace(0.5, 0.5, num=1)": I tell the model to run for one value between 
0.5 and 0.5, which is the same thing as asking it to run for 0.5. Just remember 
to change both values (e.g. the two "0.5" values at the beginning and at the 
end of the range) if you want to experiment with different values of omega or 
aspirations.
'''

## Initial aspiration level € [0,1]
aspiration_levels = np.linspace(0.5, 0.5, num=1) # The 'num' option is the number of equally spaced numbers which we want to return within the range
## Designer's accuracy
#omega_levels = np.linspace(0.5, 0.5, num=1) # Alternative with equally spaced intervals
omega_levels = np.array([0.5])
## Formal-Informal ratio (influence of D/inertial influence of past R) € [0,1] (0 = only R matters, 1 = only D matters)
w_levels = np.linspace(0, 1, num=11) # num=21 in the paper, for more granular results
## Exploration rate (when performance is below aspirations)
# This will be the average beta: when the performance discrepancy (A - P) is the highest, beta will be the double of this value (beta increases linearly from zero to 2*beta)
beta_levels = np.ceil(np.linspace(0, 0.5, num=2)*1000)/1000 # Meaningful increments of beta are only in terms of the number of agents

## Environmental shocks
shocks = 1 # Are there shocks or not
shock_type = 1 # 0 = probabilistic, 1 = fixed periods
avg_shock = 3 # if shock_tyoe == 0, specify the average number of shocks per run of the model
shock_periods = [50, 100, 150, 200, 250] # If shock_type ==1, then specify a list of periods when shocks happen

## Designer's adaptation to shocks
designer_adapt = 1 # Does the designer draw a new D (with same omega) when an environmental shock happens?

## Is beta a continuous function of performance discrepancies?
continuous_beta = 0

## Interdependence structure (E)
E_density = 0.5 # density of the interdependence structure
p_recip = 1 # percentage of reciprocal interdependences (vs. sequential)

## Cost of errors of omission and commission
omm = 1
comm = 1

## The initial realized network is determined jointly by D and a random network of density:
R_random_density = 0.5

GLOBAL_STORAGE_PERF = np.zeros((len(aspiration_levels),len(omega_levels),len(w_levels),len(beta_levels)))
GLOBAL_STORAGE_CUMUL = np.zeros((len(aspiration_levels),len(omega_levels),len(w_levels),len(beta_levels)))
GLOBAL_STORAGE_CONV = np.zeros((len(aspiration_levels),len(omega_levels),len(w_levels),len(beta_levels)))
GLOBAL_STORAGE_OMM = np.zeros((len(aspiration_levels),len(omega_levels),len(w_levels),len(beta_levels)))
GLOBAL_STORAGE_COMM = np.zeros((len(aspiration_levels),len(omega_levels),len(w_levels),len(beta_levels)))
GLOBAL_STORAGE_ASP = np.zeros((len(aspiration_levels),len(omega_levels),len(w_levels),len(beta_levels)))
GLOBAL_STORAGE_CHURN = np.zeros((len(aspiration_levels),len(omega_levels),len(w_levels),len(beta_levels)))

for aspiration_index in range(len(aspiration_levels)): # I use indexes instead of iterating directly, to use those indexes in GLOBAL_STORAGE
    aspiration = aspiration_levels[aspiration_index]
    for omega_index in range(len(omega_levels)):
        omega = omega_levels[omega_index]
        
        filename = name_this_file()
        
        # Storage for "period by period" graphs
        perf_t_by_t = np.zeros((len(w_levels),len(beta_levels), T+1))
        
        for w_index in range(len(w_levels)):
            w = w_levels[w_index]
            for beta_index in range(len(beta_levels)):
                beta = beta_levels[beta_index]
                
                ## Storage for Excel output
                
                PERF_GLOBAL = np.zeros((RUNS,T+1)) # Stores the average performance in each period, for each run
                OMM_GLOBAL = np.zeros((RUNS,T+1)) # Same, for errors of ommission
                COMM_GLOBAL = np.zeros((RUNS,T+1)) # Same, for errors of commission
                CHURN_GLOBAL = np.zeros((RUNS,T+1)) # Same, for network churn (i.e. 1- stability)
                CONV_GLOBAL = np.zeros((RUNS,T+1)) # Same, for convergence between R and D
                ASP_STATUS_GLOBAL = np.zeros((RUNS,T+1)) # Were the agents above aspirations most of the time?
                
                for run in range(RUNS):
                
                    ## Setting up storage
                    A = np.zeros((T+1,M))                
                    E = np.zeros((T+1,M,M))
                    D = np.zeros((T+1,M,M))                    
                    F = np.zeros((T+1,M,M)) # Friend requests sent in all periods (initialized here)
                    R = np.zeros((T+1,M,M)) # Realized social ineractions in all periods (initialized here)                    
                    P = np.zeros((T+1,M))
                    NB_OMMISSION = np.zeros(T+1)
                    NB_COMMISSION = np.zeros(T+1)
                    R_STABILITY = np.zeros(T+1) # Stability of realized relationships (year to year)
                    ASP_STATUS = np.zeros(T+1) # Aspirations (individual + average)
                    AVG_PERFORMANCE = np.zeros(T+1) # Average performance
                    EVO_PERFORMANCE = np.zeros(T+1) # Evolution of performance
                    CONV_R_D = np.zeros(T+1) # Convergence between R and D
                    SHOCKS_LIST = [] # List of periods where a shock happened
                
                    ### SETTING UP THE INITIAL MATRICES AT t=0
                    
                    ## Aspiration level "A", initially random (between 0 and 1)
                    A[0] = aspiration
                    ## Real EI structure "E"
                    E[0] = generate_new_task_structure()
                    ## Distance "D"
                    D[0] = designer_adapts_to(E[0])
                    ## Realized interactions "R" (initially random)
                    R_random = new_random_network(density=R_random_density)
                    F[0]= agents_determine_attractiveness(D[0], R_random)[0]
                    R[0]= agents_determine_attractiveness(D[0], R_random)[1]
                    ## Performance "P"
                    P[0] = performance_of_agents(R[0], E[0])[0]
                    NB_OMMISSION[0] = performance_of_agents(R[0], E[0])[1]
                    NB_COMMISSION[0] = performance_of_agents(R[0], E[0])[2]
                    
                    # Initial calculations
                    CONV_R_D[0] = 1-(np.count_nonzero(D[0]-R[0])/(M**2))
                    AVG_PERFORMANCE[0] = np.round(np.average(P[0]),3)
                    asp_diff = P[0]-A[0]
                    asp_diff[asp_diff>0]=0
                    below_asp = np.count_nonzero(asp_diff)
                    asp_diff[asp_diff==0]=1
                    total_asp = np.count_nonzero(asp_diff)
                    ASP_STATUS[0] = (total_asp-below_asp)/total_asp
                    R_STABILITY[0] = np.nan
                    EVO_PERFORMANCE[0] = np.nan
                    
                    ### ITERATING FOR EACH PERIOD
                    # Note: in the loops, [t] is a reference to the previous period while [t+1] refers to the present
                    
                    # for Period t= 1 to T:
                    for t in range(T):
                        
                        # Determine new E and D if necessary
                        
                        if shocks == 0:
                            E[t+1] = E[t]
                            D[t+1] = D[t]
                            
                        elif shocks == 1 and shock_type == 0:
                            shock_prob = np.random.rand()
                            if shock_prob > avg_shock / T:
                                E[t+1] = E[t]
                                D[t+1] = D[t]
                            elif shock_prob <= avg_shock / T:
                                SHOCKS_LIST.append(t+1) # Recording that there was a shock in period t+1
                                E[t+1] = generate_new_task_structure()
                                        
                        elif shocks == 1 and shock_type == 1:
                            if t+1 not in shock_periods:
                                E[t+1] = E[t]
                                D[t+1] = D[t]
                            elif t+1 in shock_periods:
                                SHOCKS_LIST.append(t+1)
                                E[t+1] = generate_new_task_structure()
                                        
                        else:
                            print('Problem: invalid value for "shocks"')
                        
                        # Adaptation by the designer or not
                        if t+1 in SHOCKS_LIST and designer_adapt == 1:
                            D[t+1] = designer_adapts_to(E[t+1])
                        elif t+1 in SHOCKS_LIST and designer_adapt == 0:
                            D[t+1] = D[t]
                        elif t+1 not in SHOCKS_LIST:
                            pass
                        else:
                            print('Problem: invalid value for "designer_adapts"')

                        # Choices by agents
                        F[t+1]= agents_determine_attractiveness(D[t+1], R[t])[0] # we only use the first returned value (the coincidence of friend requests is done later)
                        for m in range(M):
                            # if P(t-1)< A(t-1):
                            if P[t][m] < A[t][m]:
                                agent_explores(F[t+1][m], A[t][m], P[t][m])
                        
                        # Aspirations stay the same
                        A[t+1] = A[t]
 
                        # compute new interaction structure and R(t) based on double coincidence of friend requests (i.e. =1 only if agents i and j both make friend requests to each other)
                        R[t+1] = np.trunc((F[t+1] + np.transpose(F[t+1]))/2)
                        
                        # Compute the new performance
                        P[t+1] = performance_of_agents(R[t+1], E[t+1])[0]
                        NB_OMMISSION[t+1] = performance_of_agents(R[t+1], E[t+1])[1]
                        NB_COMMISSION[t+1] = performance_of_agents(R[t+1], E[t+1])[2]
                        
                        # And new convergence and stability
                        CONV_R_D[t+1] = 1-(np.count_nonzero(D[t+1]-R[t+1])/(M**2))
                        R_STABILITY[t+1] = np.round(1- np.count_nonzero(R[t+1]-R[t])/((M-1)**2),3)
                            
                        #AVG_ASPIRATIONS[t+1] = np.round(np.average(A[t+1]),3)
                        AVG_PERFORMANCE[t+1] = np.round(np.average(P[t+1]),3)
                        EVO_PERFORMANCE[t+1] = np.round(np.average(P[t+1]-np.average(P[t])),3)
                        asp_diff = P[t+1]-A[t+1]
                        asp_diff[asp_diff>0]=0
                        below_asp = np.count_nonzero(asp_diff)
                        asp_diff[asp_diff==0]=1
                        total_asp = np.count_nonzero(asp_diff)
                        ASP_STATUS[t+1] = (total_asp-below_asp)/total_asp
                    
                    PERF_GLOBAL[run] = AVG_PERFORMANCE
                    OMM_GLOBAL[run] = NB_OMMISSION
                    COMM_GLOBAL[run] = NB_COMMISSION
                    CHURN_GLOBAL[run] = 1 - R_STABILITY
                    CHURN_GLOBAL[run,0] = 0 # I am putting zero instead of missing, because otherwise the computation gets stuck
                    CONV_GLOBAL[run] = CONV_R_D # I am just calculating convergence for the end of the run
                    ASP_STATUS_GLOBAL[run] = np.round(ASP_STATUS,3)
                    
                append_to_global_storage() # see definition
                
                # Report progress
                progress = (aspiration_index*len(omega_levels)*len(w_levels)*len(beta_levels) + omega_index*len(w_levels)*len(beta_levels) + 
                    w_index*len(beta_levels) + (beta_index+1))/(len(aspiration_levels)*len(omega_levels)*len(w_levels)*len(beta_levels))
                elapsed_time = time() - start
                print(str(np.trunc(progress*100)),"% of results have been computed." + ' Time: ' + str("%.2f" % elapsed_time) + ' sec')

        ## EXPORT FOR TABLES AND GRAPHS
        #store_excel()
        store_pdf()
       
print ('\a') # This is supposed to ring the system bell, but doesn't work...
elapsed_time = time() - start
print(' time: ' + str("%.2f" % elapsed_time) + ' sec')

# Save data of this run in Python file        
#GLOBAL_STORAGE = np.array([GLOBAL_STORAGE_PERF,GLOBAL_STORAGE_CUMUL,GLOBAL_STORAGE_CONV,GLOBAL_STORAGE_OMM,GLOBAL_STORAGE_COMM,GLOBAL_STORAGE_ASP, GLOBAL_STORAGE_CHURN])
#storage_file_name = str('matrix ' + ' runs_' + str(RUNS)  + ' M_' + str(M) + ' ' + ' s'*shocks + '_ad '*designer_adapt + ' cbeta'*continuous_beta + ' ' + date)
#np.save(str(folder + storage_file_name + '.npy'),GLOBAL_STORAGE) 