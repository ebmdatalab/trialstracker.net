import os

from fabric.api import run, sudo
from fabric.api import prefix, warn, abort
from fabric.api import task, env
from fabric.contrib.files import exists
from fabric.context_managers import cd

env.hosts = ['smallweb1.openprescribing.net']
env.forward_agent = True
env.colorize_errors = True

environments = {
    'live': 'trialstracker.net',
}

def sudo_script(script, www_user=False):
    """Run script under `deploy/fab_scripts/` as sudo.

    We don't use the `fabric` `sudo()` command, because instead we
    expect the user that is running fabric to have passwordless sudo
    access.  In this configuration, that is achieved by the user being
    a member of the `fabric` group (see `setup_sudo()`, below).

    """
    if www_user:
        sudo_cmd = 'sudo -u www-data '
    else:
        sudo_cmd = 'sudo '
    return run(sudo_cmd +
        os.path.join(
            env.path,
            'trialstracker.net/deploy/fab_scripts/%s' % script)
    )

def setup_sudo():
    """Ensures members of `fabric` group can execute deployment scripts as
    root without passwords

    """
    sudoer_file = '/etc/sudoers.d/trialstracker_fabric_{}'.format(env.app)
    if not exists(sudoer_file):
        sudo('echo "%fabric ALL = (www-data) NOPASSWD: {}/trialstracker.net/deploy/fab_scripts/" > {}'.format(env.path, sudoer_file))

def make_directory():
    if not exists(env.path):
        sudo("mkdir -p %s" % env.path)
        sudo("chown -R www-data:www-data %s" % env.path)
        sudo("chmod  g+w %s" % env.path)

def update_from_git(branch):
    # clone or update code
    if not exists('trialstracker.net/.git'):
        run("git clone -q git@github.com:ebmdatalab/trialstracker.net.git")
    with cd("trialstracker.net"):
        run("git fetch --all")
        run("git reset --hard origin/{}".format(branch))

def setup_nginx():
    sudo_script('setup_nginx.sh %s %s' % (env.path, env.app))

def reload_nginx():
    sudo_script("reload_nginx.sh")

def setup(environment, branch='master'):
    if environment not in environments:
        abort("Specified environment must be one of %s" %
              ",".join(environments.keys()))
    env.app = environments[environment]
    env.environment = environment
    env.path = "/var/www/%s" % env.app
    env.branch = branch
    return env


@task
def deploy(environment, branch='master'):
    env = setup(environment, branch)
    make_directory()
    setup_sudo()
    with cd(env.path):
        update_from_git(branch)
        setup_nginx()
        reload_nginx()
