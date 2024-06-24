import os
import subprocess
import yaml

def read_cred_file(file_path):
    env_data = {}
    with open(file_path, "r") as file:
        for line in file:
            line = line.strip()  # Remove leading/trailing whitespaces
            if line and not line.startswith("#"):  # Ignore empty lines and comments
                key, value = line.split("=")  # Split the line by '='
                env_data[key.strip()] = value.strip()  # Remove leading/trailing whitespaces and store key-value pair
    return env_data

def check_file_existence(directory, filename):
    # Construct the full path to the file
    file_path = os.path.join(directory, filename)
    
    # Check if the file exists
    if os.path.exists(file_path):
        print(f"The file '{filename}' exists in the directory '{directory}'.")
        return True
    else:
        print(f"The file '{filename}' does not exist in the directory '{directory}'.")


def create_and_get_sealed_secret(cred):
    secret_name= input("Give a name you want your cridential to be identified as: ")

    command = f'kubectl create secret generic {secret_name}'
    for key, value in cred.items():
        command += f' --from-literal={key}={value}'

        command += f' -o yaml > {secret_name}.yaml'
    output = subprocess.run(command, shell=True, capture_output=True, text=True)
    # Check if the command was successful
    if output.returncode == 0:
        #use generated yaml file to generate a sealed secret file
        kubeseal_command= f'kubeseal -f {secret_name}.yaml -w {secret_name}_sealed.yaml'
        subprocess.run(kubeseal_command, shell=True, capture_output=True, text=True)

        #use generated sealed secret file to create a sealed-secret resource in the cluster
        kubectl_command= f'kubectl create -f {secret_name}_sealed.yaml'
        subprocess.run(kubectl_command, shell=True, capture_output=True, text=True)

        with open(f"{secret_name}_sealed.yaml","r") as file:
            sealed_secret_data = yaml.safe_load(file)

        secrets_from_sealed_file = sealed_secret_data["spec"]["encryptedData"]


        
        with open("generated_secrets.txt", "w") as file:
            for key, value in secrets_from_sealed_file.items():
                file.write(f"{key}: {value}\n")
    else:
        print("Command failed.")
        print("Error message:")
        print(output.stderr)

# Get user input from the terminal
user_input = input("Do you have a .env file containning all your cridentials(Yy/Nn): ")

if user_input == "Y" or user_input == "y":
    print("Input full path to the folder your .env file is located('/path/to/your/folder')")
    directory= input("If you are in the directory where the .env file is located just use a '.' as the full file path: ")
    filename= "./.env"
    file_exits= check_file_existence(directory, filename)

    if file_exits:
        env_data= read_cred_file(f"{directory}/{filename}")

        generated_sealed_secret= create_and_get_sealed_secret(env_data)
elif user_input == "N" or user_input == "n":
    print("Input 'stop' to stop inputing your credentials.")
    # Create an empty file
    with open('new.txt', 'w'):
        pass

    while True:
        cred_input= input("Input your credentials is this format 'key=value' or 'stop' to stop inputing your credentials: ")
        
        if cred_input.lower() == "stop":
            break
        else:
            if "=" in cred_input:
            #append credentials to created file
                with open('new.txt', 'a') as f:
                    f.write(f"{cred_input}\n")
            else:
                print("Please your credential input should be in the form of 'key=value'!")

    cred_data= read_cred_file("new.txt")
    generated_sealed_secret= create_and_get_sealed_secret(cred_data)

    # Delete the file
    os.remove("new.txt")
            
        
else:
    print("Please input Yy/Nn")

    





