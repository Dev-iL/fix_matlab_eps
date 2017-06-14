function fix_matlab_eps(input_file, output_file, inkscape_binary_path)
% MATLAB wrapper for fix_matlab_eps.py
% By Dev-iL, 2017

if nargin < 2
  throw(MException('fix_matlab_eps:InsufficientInputs',...
                   'You must specify an input and an output filename.'));
end
if nargin < 3
  inkscape_binary_path = 'inkscape';
end
% Import the python script:
fme = py.importlib.import_module('fix_matlab_eps');
% Run the python script:
try
  fme.fix_eps(['"' input_file '"'], ['"' output_file '"'], ['"' inkscape_binary_path '"']);
catch % Fallback in case the python interface isn't working.
  system(['python ' fullfile(fileparts(mfilename('fullpath')),'fix_matlab_eps.py')...
          ' "' input_file '" "' output_file '" "' inkscape_binary_path '"']);
end