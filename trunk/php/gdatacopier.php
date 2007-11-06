<?php

/*
    GDataCopier.php, Copyright (c) 2007 Eternity Technologies Pty Limited
    <http://code.google.com/p/gdatacopier/>
    Distributed under the terms and conditions of the GNU/GPL v2
    
    Written by: Devraj Mukherjee <devraj@gmail.com>
    
    Based on the Python library published as part of the GDataCopier project.
    
    This is FREE SOFTWARE and comes with NO WARRANTY, use of this software 
    is completely at your OWN RISK.
    
    This class library was written for PHP5 and tested under Linux systems.
    It also requires the HTTP_Client PEAR package which can be acquired from
    
    http://pear.php.net/package/HTTP_Client/

 */
 
require_once 'HTTP/Client.php';
require_once 'HTTP/Client/CookieManager.php';

/*
    The following classes are designed to ease writing code with GDataCopier
 */

class GoogleDocFormat
{
    public $OOWriter  = "oo";
    public $MSWord    = "doc";
    public $RichText  = "rtf";
    public $Text      = "txt";
    public $PDF       = "pdf";
}


class GoogleSpreadsheetFormat
{
    public $MSExcel   = "xls";
    public $CSV       = "csv";
    public $Text      = "txt";
    public $OOCalc    = "ods";
}

/*
    GDataCopier, the main class that implements functionality described in
    the Wiki documents
 */

class GDataCopier
{
    private $_http_client;
    private $_is_hosted;
    private $_is_logged_on;
    
    private $_url_google_auth      = "https://www.google.com/accounts/ServiceLoginAuth";
    private $_url_google_followup  = "https://docs.google.com";
    private $_url_google_get_doc   = "https://docs.google.com/MiscCommands?command=saveasdoc&exportformat=%format&docID=%docId";
    private $_url_google_get_sheet = "https://spreadsheets.google.com/ccc?output=%format&key=%docId";
    
    /*
   
      If you are using Google hosted applications the URLs are somewhat different
      these variables hold the pattern, and the API switches accordingly
      
    */
    
    private $_url_hosted_auth      = "https://www.google.com/a/%domain/LoginAction";
    private $_url_hosted_followup  = "https://docs.google.com/a/%domain/";
    private $_url_hosted_get_doc   = "https://docs.google.com/a/%domain/MiscCommands?command=saveasdoc&exportformat=%format&docID=%docId";
    private $_url_hosted_get_sheet = "https://spreadsheets.google.com/a/%domain/pub?output=%format&key=%docId";
    
    public function GDataCopier()
    {
        $this -> logout();
    }
    
    public function logout()
    {
        $this -> _http_client   = &new HTTPClient();
        $this -> _is_hosted     = False;
    }
    
    public function set_proxy($proxy_host, $proxy_port, $proxy_username = Null, $proxy_password = Null)
    {
        $this -> _http_client -> setRequestParameter('proxy_host', $proxy_host);
        $this -> _http_client -> setRequestParameter('proxy_port', $proxy_port);
        
        /* These two parameters are optional */
        if($proxy_username != Null)
            $this -> _http_client -> setRequestParameter('proxy_user', $proxy_username);
        if($proxy_password != Null)
            $this -> _http_client -> setRequestParameter('proxy_pass', $proxy_password);
    
    }
    
    public function login($username, $password)
    {
        $this -> _is_logged_in = True;
        
        if($this -> do_google_login($username, $password))
            $this -> _is_hosted = False;
        elseif ($this -> do_hosted_login($username, $password))
            $this -> _is_hosted = True;
        else
            $this -> _is_logged_in = False;
    }
    
    
    public function export_metadata($document_id, $metadata_filename)
    {
        /* We will have to fetch the Atom feed to get this working */
    
    }
    
    
    public function import_document($document_path, $title)
    {
        /* We will have to fetch the Atom feed to get this working */
    
    }
    
    public function export_document($document_id, $document_path)
    {
    
    
    }
    
    
    public function export_spreadsheet($document_id, $document_path)
    {
    
    
    }
    
    /*
        Various private methods to help the API function
     */
     
    private function do_google_login($username, $password)
    {
        $login_data = array();
        $login_data['PersistentCookies']    = 'true';
        $login_data['Email']                = $username;
        $login_data['Passwd']               = $password;
        $login_data['continue']             = $this -> _url_google_followup;
        $login_data['followup']             = $this -> _url_google_followup;
        
        $this -> _http_client -> post($this -> _url_google_auth, $login_data);

    }
    
    private function do_hosted_login($emailAddress, $password)
    {
        list($username, $domain_name) = split("@", $emailAddress);
        
        $login_data = array();
        $login_data['persistent']   = 'true';
        $login_data['userName']     = $username;
        $login_data['password']     = $password;
        $login_data['continue']     = $this -> _url_google_followup;
        $login_data['followup']     = $this -> _url_google_followup;
        
        $prepared_url = strreplace($this -> _url_hosted_auth, "%domain", $domain_name);
        $this -> _http_client -> post($prepared_url, $login_data);
  
    }

}

/* 
    End of PHP library file
 */
 
?>
