#!/usr/bin/env python
#
#  gdatacopier, Command line utilties to manage your Google docs
#  http://gdatacopier.googlecode.com
#
#  Copyright (c) 2012, Eternity Technologies Pty Ltd.
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#  

__all__ = ['auth']

try:
    import argparse
except:
    print "gdc can't find core Python components, please validate your environment"

## @defgroup exception Exception defined by GDataCopier
#


## @brief Sets up the Argparser for GDataCopier
#
class ParserBuilder(object):
    
    ## @brief Sets up a Subparser for the logout command
    #
    #  @ingroup parsers
    #
    def setup_mkdir_subparser(self, subparsers):

        mkdir_parser = subparsers.add_parser(
            "mkdir", 
            help="creates folders on Google doc servers")

    ## @brief Sets up a Subparser for the logout command
    #
    #  @ingroup parsers
    #
    def setup_delete_subparser(self, subparsers):

        delete_parser = subparsers.add_parser(
            "delete", 
            help="deletes objects on Google doc servers")

    ## @brief Sets up a Subparser for the logout command
    #
    #  @ingroup parsers
    #
    def setup_list_subparser(self, subparsers):

        list_parser = subparsers.add_parser(
            "list", 
            help="lists / queries objects on the Google doc servers")

    ## @brief Sets up a Subparser for the logout command
    #
    #  @ingroup parsers
    #
    def setup_copy_subparser(self, subparsers):

        copy_parser = subparsers.add_parser(
            "copy", 
            help="bi-directional copy of accepted documents")

    ## @brief Sets up a Subparser for the logout command
    #
    #  @ingroup parsers
    #
    def setup_logout_subparser(self, subparsers):

        logout_parser = subparsers.add_parser(
            "logout", 
            help="unregisters two legged authentication credentials")

    ## @brief Sets up a Subparser for the login command
    #
    #  @ingroup parsers
    #
    def setup_login_subparser(self, subparsers):

        login_parser = subparsers.add_parser(
            "login", 
            help="registers and validates two legged authentication, use Google API console to obtain credentials")

        login_parser.add_argument(
            '--consumer-secret', '-s', 
            help="Consumer secret obtained from Google API console", 
            action='store',
            required=True, 
            dest='consumer-secret')

        login_parser.add_argument(
            '--client-id', '-c', 
            help="Client ID obtained from Google API console", 
            action='store', 
            required=True,
            dest='consumer-id')

        login_parser.add_argument(
            '--username', '-u',
            help="default username to use when interacting with Google doc servers, overridden by command line value",
            action='store',
            required=False,
            dest='username')


    ## @brief Sets up the ArgParser and command line rules
    #
    #  @ingroup parsers
    #
    def setup_args_parser(self):

        arg_parser = argparse.ArgumentParser(
            prog="gdc", 
            description="command line tool to automate management of Google docs.", 
            epilog="gdatacopier comes with ABSOLUTELY NO WARRANTY. This is free software, and you are welcome to redistribute it under the conditions of the GNU GPLv2.")

        subparsers = arg_parser.add_subparsers(dest="subparser_name")

        # Setup various sub parsers / commands offered by gdc
        self.setup_login_subparser(subparsers)
        self.setup_logout_subparser(subparsers)
        self.setup_copy_subparser(subparsers)
        self.setup_list_subparser(subparsers)
        self.setup_delete_subparser(subparsers)
        self.setup_mkdir_subparser(subparsers)

        return arg_parser