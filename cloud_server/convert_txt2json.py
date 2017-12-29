import json, os

def main():
    path = './movie_details.json'
    movie_details_f = open(path)

    json_list = []
    for movie_details in movie_details_f.readlines():
        json_details = json.loads(movie_details)
        json_list.append(json_details)

    json_list_output = json.dumps(json_list)
    with open('./movie_details_array.json', 'a') as outfile:
        outfile.write(json_list_output)

if __name__ == "__main__":
    main()

