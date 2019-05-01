import os
import shutil
import pydot
from lxml import html
from fastensource.utils.helpers import delay, execute_command,\
        requests_get_handler


def get_name(artifact, version, filetype, org=''):
    """Get a name in maven's central format.
    """
    return org + artifact + '-' + version + '.' + filetype


def get_url(package, version, extension):
    """Get the url for a file from central.maven.org.

    """
    url = ''
    project = package.split(':')[0]
    for el in project.split('.'):
        url += el + '/'
    artifact = package.split(':')[1]
    url += artifact + '/'
    url += version + '/'
    name = get_name(artifact, version, extension)
    url += name
    return url


@delay
def find_last_version(url_v, package, delay):
    """Find the last release of a package.

    Args:
        url_v (str): Url to make the request.
        pakcage (str): Package name
        delay (int): Seconds to wait

    """
    url = url_v + package.split(':')[0] + '/' + package.split(':')[1]
    page = requests_get_handler(url)
    if page.status_code == 404:
        return 'Error'
    tree = html.fromstring(page.content)
    element = '//a[@class="vbtn release"]//text()'
    elements = tree.xpath(element)
    if len(elements) == 0:
        return 'Not Found'
    return elements[0]


@delay
def download_maven_jar(url, package, version, delay):
    """Download maven project jar.

    """
    filename = get_name(package.split(':')[1], version, 'jar',
                        package.split(':')[0] + '.')
    url = url + get_url(package, version, 'jar')
    r = requests_get_handler(url)
    if r.status_code == 404:
        # FIXME
        print('Error: ' + url + ' Not Found\n')
    with open(filename, 'wb') as f:
        f.write(r.content)


@delay
def get_pom_xml(url, project, version, delay):
    """Get the pom of a project.

    Args:
        url (str): URL to make the request
        project (str): Project name
        version (str): Project version
        delay (str): Second to sleep

    Returns:
        content (str): The contents of pom xml file.

    """
    url = url + get_url(project, version, 'pom')
    r = requests_get_handler(url)
    if r.status_code == 404:
        # FIXME
        print('Error: ' + url + ' Not Found\n')
    return r.content


@delay
def find_dependencies(pom_content, delay):
    """Find the dependencies of a maven project using mvn.

    Args:
        pom_content (str): pom xml's content
        delay (int): seconds to sleep

    Returns:
        dependencies (list): of tuples with project, version.

    """
    dependencies = list()
    # tempfile doesn't work here!!!
    os.makedirs('temp')
    os.chdir('temp')
    with open('pom.xml', 'wb') as f:
        f.write(pom_content)
    cmd = ('mvn '
           'org.apache.maven.plugins:maven-dependency-plugin:2.4:tree '
           '-DoutputFile=deps.dot -DoutputType=dot'
           )
    # FIXME
    exit_code = execute_command(cmd)
    if exit_code == 0:
        graphs = pydot.graph_from_dot_file('deps.dot')
        graph = graphs[0]
        for edge in graph.get_edge_list():
            dest = edge.get_destination().replace('"', '')
            package = dest.split(':jar:')[0]
            version = dest.split(':jar:')[1].split(':')[0]
            dependencies.append(tuple([package, version]))
    os.chdir('..')
    shutil.rmtree('temp')
    return dependencies
