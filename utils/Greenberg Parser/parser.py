######
# Parses and processes data from Greenberg, S. (1988). "Using Unix: collected traces of 168 users" dataset.
# Format is defined to mimic the experimental setup used in Logical Hidden Markov Models paper by Kersting et al.
# ---
# Usage: python parser.py
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

			# Check if alias is in lohmm_commands
			if aliases[i].split(' ')[0] in lohmm_commands:

				# Throw away bad mkdir commands
				if aliases[i].split(' ')[0] == 'mkdir' and len(aliases[i].split(' ')) == 1:
					full_commands.append('com')
				
				else:
					full_commands.append(aliases[i])
			
			else:
				full_commands.append('com')

		else:

			# Check if user command is in lohmm_commands
			if commands[i].split(' ')[0] in lohmm_commands:

				# Throw away bad mkdir commands
				if commands[i].split(' ')[0] == 'mkdir' and len(commands[i].split(' ')) == 1:
					full_commands.append('com')

				else:
					full_commands.append(commands[i])

			else:
				full_commands.append('com')		

	return full_commands

###
# Function checks if a session is valid by checking if at least one command was mkdir with a correct number of args
###
def is_valid_session(session):

	for command in session:

		if command.split(' ')[0] == 'mkdir':
			return True

	return False

###
# Function removes pipes and flags from a command sequence.
###
def simplify_commands(commands):

	# Clean commands to remove pipes, flags, etc
	for i in range(len(commands)):

		# If there is a pipe in the command take the prefix of the command
		if '|' in commands[i]:
			commands[i] = commands[i].split('|')[0]

		# Remove multiple commands
		if ';' in commands[i]:
			commands[i] = commands[i].split(';')[0]

		# Remove & from commands
		if '&' in commands[i]:
			commands[i] = commands[i].split('&')[0]

		# Remove all flags from command
		commands[i] = re.sub(r'-\w* ?', '', str(commands[i]))

###
# Function rewrites commands which are not preceeded in 10 timesteps by 'mkdir' to 'com'.
# First we find the indices where 'mkdir' appears
# Then for each index we add the next 10 indices to the valid domain
# All indices not in the valid domain will have the command set to 'com'
###
def rewrite_bad_commands(commands):
	mkdir_indices = []
	valid_indices = []

	# Find where each 'mkdir' appears
	for i in range(len(commands)):
		if commands[i].split(' ')[0] == 'mkdir':
			mkdir_indices.append(i)

			# Add the current i and the next 10 positions to the valid domain
			for j in range(0, 11):
				valid_indices.append(i + j)

	# Rewrite all bad commands to 'com'
	for i in range(len(commands)):
		if i not in valid_indices:
			commands[i] = 'com'

	if len(valid_indices) > 0:
		return True

	return False

###
# Function rewrites all paths to be absolute valued using the current directory data.
# Returns set of all directories found in current command stream.
###
def rewrite_directories(commands, directories):
	base = ''  # Base directory

	# Find the base directory
	for i in range(len(directories)):
		
		if len(base) == 0:
			base = re.findall(r'/user/\w*/\w*', directories[i])

			if base:
				base = base[0]
				break

	# Rewrite each command
	for i in range(len(commands)):
		
		if commands[i] != 'com':
			command = commands[i].split(' ')

			# Remove whitespace artifacts
			if command[-1] == '':
				del command[-1]
			
			# {ls, cd} commands with no path given
			if len(command) == 1:
				
				# An empty dir for 'cd' is a 'cd' to the base dir
				if command[0] == 'cd':
					commands[i] = commands[i] + ' ' + base

				# An empty dir for 'ls' is an 'ls' the current dir
				elif command[0] == 'ls':
					commands[i] = commands[i] + ' ' + directories[i]

				# Rewrite ill-formed commands to com
				else:
					commands[i] = 'com'

			# {ls, cd, mkdir} commands
			elif len(command) == 2:

				# {ls, cd, mkdir} commands with a relative path
				if command[0] in ['ls', 'cd', 'mkdir']:
					
					# Rewrite commands without special paths
					if not command[1][0] in ['/', '.', '~']:
						
						# Simply prepend the current directory to the command
						# EX: cd next -> cd cur/next
						if directories[i] != '/':
							command[1] = directories[i] + '/' + command[1]
						else:
							command[1] = directories[i] + command[1]

					# Handle ~ paths
					elif command[1][0] == '~':
						command[1] = rewrite_tilde(command[1], base)

					# Handle / paths
					elif command[1][0] == '/':

						# / paths are already absolute, but we will make the /user/ uniform
						command[1] = re.sub(r'/user\w/', '/user/', command[1])

					# Handle . paths
					elif command[1][0] == '.':
						command[1] = rewrite_dot(command[1], base, directories[i])

					commands[i] = ' '.join(command)
			
				# Rewrite ill-formed commands to com
				else:
					commands[i] = 'com'

			# {cp, mv} commands
			elif len(command) == 3:

				# {cp, mv} commands with relative paths
				if command[0] in ['cp', 'mv']:

					# Apply rewriting logic
					for j in range(1, 3):

						# Rewrite commands without special paths
						if not command[j][0] in ['/', '.', '~']:
							
							# Simply prepend the current directory to the command
							# EX: cd next -> cd cur/next
							if directories[i] != '/':
								command[j] = directories[i] + '/' + command[j]
							else:
								command[j] = directories[i] + command[j]

						# Handle ~ paths
						elif command[j][0] == '~':
							command[j] = rewrite_tilde(command[j], base)

						# Handle / paths
						elif command[j][0] == '/':

							# / paths are already absolute, but we will make the /user/ uniform
							command[j] = re.sub(r'/user\w/', '/user/', command[j])

						# Handle . paths
						elif command[j][0] == '.':
							command[j] = rewrite_dot(command[j], base, directories[i])

					commands[i] = ' '.join(command)

				# Rewrite ill-formed commands to com
				else:
					commands[i] = 'com'

			# Rewrite ill-formed commands to com
			else:
				commands[i] = 'com'

###
# Rewrites tilde paths
###
def rewrite_tilde(command, base):

	# A single ~ path is the base
	if len(command) == 1:
		command = base

	else:

		# When dir is ~ABC the dir is user ABC base dir
		if command[1] != '/':
			command = re.findall(r'/user/\w*/', base)[0] + command[1:]

		# When dir is ~/ABC the dir is base/ABC
		else:
			command = base + command[1:]

	return command

###
# Rewrites paths starting with .
###
def rewrite_dot(command, base, current_dir):

	# . path means current dir
	if len(command) == 1:
		command = current_dir

	# .. in path means previous dir
	elif command[1] == '.':
		split = command.split('/')
		count = command.count('..')
		prev = '/'.join(current_dir.split('/')[:-count])
		next = '/'.join(split[count:])

		if next:
			command = prev + '/' + next
		else:
			command = prev

	# If the dir is a .abc filename, use the current dir
	else:
		command = current_dir + '/' + command

	return command

###
# Main
# ---
# For each data file...
#     Split the data text into user sessions
#     Filter out relevant data: commands, aliases, and working directories
#     Rewrite the command sequence into full non-aliased form
#     Remove invalid sessions without mkdir appearing at least once
#     Rewrite invalid commands (those which do not have a mkir within 10-timesteps prior) to com
#     Simplify the resulting commands by removing pipes and switches
#     Rewrite directories to be absolute path names
###
data_dir = '../../../Data/UnixData/unix-data/computer-scientists/scientist-'  # Relative location of dataset
lohmm_commands = ['mkdir', 'ls', 'cd', 'cp', 'mv']  # Valid LOHMM commands

# Data Structures
session_streams = []
sessions = []  # List of session data dicts with keys = {'commands', 'aliases', 'directories'}
valid_sessions = []

# Read file data
for i in range(1, 53):
	with open(data_dir + str(i), 'r') as f:	
		session_streams = session_streams + f.read().split('\nS')  # Split data into session streams

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

	# Remove invalid sessions (those without mkdir)
	if is_valid_session(sessions[i]['full_commands']):
		valid_sessions.append(sessions[i])

# Create cleaned user activity stream for each session
for i in range(len(valid_sessions)):

	# Rewrite commands which did not have a mkdir within 10 time-steps preceeding
	rewrite_bad_commands(valid_sessions[i]['full_commands'])

	# Remove pipes and flags from full command sequence
	simplify_commands(valid_sessions[i]['full_commands'])

	# Make directories absolute
	rewrite_directories(valid_sessions[i]['full_commands'], valid_sessions[i]['directories'])