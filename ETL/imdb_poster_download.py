import json, os, urllib2

def downloadPhoto(folder, url, id):
    try:
        u = urllib2.urlopen(url)
        file_name = str(id) + ".jpg"
        localFile = open(os.path.join(folder, file_name), "wb")
        localFile.write(u.read())
        localFile.close()
        u.close()
    except:
        print "not found: " + str(url)


def main():
    path = '../cloud_server/movie_details.json'
    movie_details_f = open(path)

    downloadPhoto('../website/public/images/posters', 'https://images-na.ssl-images-amazon.com/images/M/MV5BMTgyNDgyNTkyNF5BMl5BanBnXkFtZTcwNTE2ODUzMQ@@._V1_SX300.jpg', '1')

    for movie_details in movie_details_f.readlines():
        json_details = json.loads(movie_details)

        if "Poster" in json_details:
            if json_details["Poster"] != "N/A":
                downloadPhoto('../website/public/images/posters', json_details['Poster'], json_details['id'])


if __name__ == "__main__":
    main()

