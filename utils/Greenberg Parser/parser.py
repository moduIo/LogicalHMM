######
# Parses and processes data from Greenberg, S. (1988). "Using Unix: collected traces of 168 users" dataset.
# Format is defined to mimic the experimental setup used in Logical Hidden Markov Models paper by Kersting et al.
######
import sys

###
# Function parses session data into sequences of commands, aliases, and directories.
###
def filter_session_data(session):
	commands = []       # Sequential list of commands in file
	aliases = []        # Sequential list of aliases in file
	directories = []    # Sequential list of directories in file

	# Parse session into sequences
	for line in session:

		# Ignore blank lines
		if len(line) > 0:

			# Store data into appropriate list without leading ID ('C ', 'A ', 'D ')
			if line[0] == 'C':
				commands.append(line[2:])

			elif line[0] == 'A':
				aliases.append(line[2:])
			
			elif line[0] == 'D':
				directories.append(line[2:])

	return commands, aliases, directories

###
# Function rewrites a command sequence from aliased to full form.
# EX: r -> rwho -a | more
###
def rewrite_aliases(commands, aliases, lohmm_commands):
	full_commands = []  # Sequential list of full commands (non-aliased) in file

	for i in range(len(commands)):
		
		if aliases[i] != 'NIL':

			# Check if command is in lohmm_commands
			if aliases[i].partition(' ')[0] in lohmm_commands:
				full_commands.append(aliases[i])

			else:
				full_commands.append('com')

		else:

			if commands[i].partition(' ')[0] in lohmm_commands:
				full_commands.append(commands[i])

			else:
				full_commands.append('com')		

	return full_commands

###
# Function removes pipes and switches from a command sequence.
###
def simplify_commands(commands):

	# Clean commands to remove pipes, switches, etc
	for i in range(len(commands)):

		# If there is a pipe in the command take the prefix of the command
		if '|' in commands[i]:
			commands[i] = commands[i].split('|')[0]

###
# Main
# ---
# For a specified data file...
#     Split the data text into user sessions
#     Filter out relevant data: commands, aliases, and working directories
#     Rewrite the command sequence into full non-aliased form
#     Simplify the resulting commands by removing pipes and switches
###
data_dir = '../../../Data/UnixData/unix-data/computer-scientists'  # Relative location of dataset
lohmm_commands = ['mkdir', 'ls', 'cd', 'cp', 'mv']                 # Valid LOHMM commands
data = sys.argv[1]                                                 # Filename to parse

# Read file data
with open(data_dir + '/' + data, 'r') as f:	
	sessions = f.read().split('\nS')  # Split data into sessions

# Split data into strings
for i in range(len(sessions)):
	sessions[i] = sessions[i].split('\n')[2:]

#
for session in sessions:
	filter_session_data(session, commands, aliases, directories)

####
#for c in full_commands:
#	if 'mkdir' in c:
#		print c