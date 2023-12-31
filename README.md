# rulemaker
The code is a Python program created by user: vasceannie that utilizes the Tkinter library to create a GUI application for transforming data from a source CSV file and saving the transformed data into an output CSV file.

The program imports the required packages: tkinter, filedialog, ttk, and pandas.

It defines three functions:

select_source_file(): This function opens a file dialog to allow the user to select the source CSV file. The selected file path is stored in the source_file_path variable.

select_output_file(): This function opens a file dialog to allow the user to select the output CSV file location. The selected file path is stored in the output_file_path variable.

transform_data(): This function processes the data from the source file and saves the transformed data into the output file. It performs the following steps:

Reads the source CSV file using the pandas read_csv() function. It specifies the SB_LIMIT_AMT column to be read as a string.
Defines a placeholder for the transformed data.
Groups the data by the columns SB_APRV_LEVEL, CSU_CALSTEDUPERSID, and BUSINESS_UNIT.
Processes each group and generates the required values for each field.
Appends the transformed data to the placeholder list.
Creates a DataFrame from the transformed data using pandas.
Saves the DataFrame to the output CSV file using the to_csv() function.
Updates the progress bar value to 100.
After defining the functions, the program creates the main application window using tk.Tk(). It sets the title of the window to "ChicoDOA Transformer - CSV".

The program initializes two variables, source_file_path and output_file_path, as tk.StringVar() to store the paths of the selected source and output files.

It creates three UI elements:

source_file_button: A button with the label "Select Source CSV" that when clicked calls the select_source_file() function.
output_file_button: A button with the label "Select Output CSV Location" that when clicked calls the select_output_file() function.
transform_button: A button with the label "Transform Data" that when clicked calls the transform_data() function.
It also creates a progress bar using ttk.Progressbar to indicate the progress of the data transformation.

Finally, the program enters the main event loop using root.mainloop() to start the GUI application.

09/19/2023 Updates by vasceannie and raparkinson2 include:
Limiting the 'deptids' elements to less than 49 so the file successfully imports. 
If the 'deptids' exceed 49, a new line is created using the same 'rule_group_internal_name' and 'rule_group_display_name' but now includes ":02" for the first 'deptids_chunk' and goes up an increment of one, each new 'chunk' of 49. 
