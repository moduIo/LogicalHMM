######
# Parses and processes data from Greenberg, S. (1988). "Using Unix: collected traces of 168 users" dataset.
# Format is defined to mimic the experimental setup used in Logical Hidden Markov Models paper by Kersting et al.
# ---
# Usage: python parser.py 'scientist-1'
######
import sys
import re

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

		# Remove all flags from command
		commands[i] = re.sub(r'-\w* ?', '', str(commands[i]))
		print commands[i]

###
# Main
# ---
# For a specified data file...
#     Split the data text into user sessions
#     Filter out relevant data: commands, aliases, and working directories
#     Rewrite the command sequence into full non-aliased form
#     Simplify the resulting commands by removing pipes and switches
###
data_dir = '../../../Data/UnixData/unix-data/computer-scientists/'  # Relative location of dataset
lohmm_commands = ['mkdir', 'ls', 'cd', 'cp', 'mv']                 # Valid LOHMM commands

# Data Structures
sessions = []  # List of session data dicts with keys = {'commands', 'aliases', 'directories'}

# Read file data
with open(data_dir + sys.argv[1], 'r') as f:	
	session_streams = f.read().split('\nS')  # Split data into session streams

# Split session streams into strings
for i in range(len(session_streams)):
	session_streams[i] = session_streams[i].split('\n')[2:]

# Filter our relevant data from activity stream
for session in session_streams:
	commands, aliases, directories = filter_session_data(session)

	# Populate dictionary values and add to sessions list
	session_values = {}
	session_values['commands'] = commands
	session_values['aliases'] = aliases
	session_values['directories'] = directories

	sessions.append(session_values)

# Create cleaned user activity stream for each session
for i in range(len(sessions)):

	# Generate rewritten command sequence
	sessions[i]['full_commands'] = rewrite_aliases(sessions[i]['commands'], sessions[i]['aliases'], lohmm_commands)

	# Remove pipes and flags from full command sequence
	simplify_commands(sessions[i]['full_commands'])

####
#for session in sessions:
#	for i in session['full_commands']:
#		print i
#	print '=======\n'