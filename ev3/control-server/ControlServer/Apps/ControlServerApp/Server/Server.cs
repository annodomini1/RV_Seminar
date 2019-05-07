using System;
using System.Net;
using System.Net.Sockets;
using System.Text;
using System.Threading;
using System.Linq;
using System.Net.NetworkInformation;
// using System.Collections.Generic;
using Message = System.Collections.Generic.Dictionary<string, string>;

using Lego.Ev3.Core;
using Lego.Ev3.Desktop;

using Server.CommInterface;

namespace Server
{ 

// State object for reading client data asynchronously
public class StateObject
{
    // Client  socket.
    public Socket workSocket = null;
    // Size of receive buffer.
    public const int BufferSize = 1024;
    // Receive buffer.
    public byte[] buffer = new byte[BufferSize];
    // Received data string.
    public StringBuilder sb = new StringBuilder();
}

    public class AsynchronousSocketListener
    {
        public static Brick _brick = null;
        public static bool _uselocalhost = false;
        private static bool _isrunning = false;
        private static Socket listener;

        // Thread signal.
        public static ManualResetEvent allDone = new ManualResetEvent(false);

        public AsynchronousSocketListener()
        {
        }

        public static bool GetState()
        {
            return _isrunning;
        }

        public static void StartListening()
        {
            // Data buffer for incoming data.
            byte[] bytes = new Byte[1024];

            // Establish the local endpoint for the socket.
            // The DNS name of the computer
            // running the listener is "host.contoso.com".
            // IPHostEntry ipHostInfo = Dns.Resolve(Dns.GetHostName());
            IPHostEntry ipHostInfo = Dns.Resolve("localhost");
            IPAddress ipAddress = _uselocalhost ? ipHostInfo.AddressList[0] : LocalIPAddress();
            IPEndPoint localEndPoint = new IPEndPoint(ipAddress, 11000);

            // Create a TCP/IP socket.
            listener = new Socket(AddressFamily.InterNetwork,
                SocketType.Stream, ProtocolType.Tcp);

            // Bind the socket to the local endpoint and listen for incoming connections.
            try
            {
                listener.Bind(localEndPoint);
                listener.Listen(100);

                // Signal running state
                _isrunning = true;

                while (_isrunning)
                {
                    // Set the event to nonsignaled state.
                    allDone.Reset();

                    // Start an asynchronous socket to listen for connections.
                    Console.WriteLine("Waiting for a connection...");
                    listener.BeginAccept(
                        new AsyncCallback(AcceptCallback),
                        listener);

                    // Wait until a connection is made before continuing.
                    allDone.WaitOne();
                }

            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }

            Console.WriteLine("\nShutting down server...");

            //// Shutdown and close socket
            //try
            //{
            //    listener.Shutdown(SocketShutdown.Both);
            //}
            //catch(Exception e)
            //{
            //    Console.WriteLine(e.ToString());
            //}

            //try 
            //{
            //    listener.Close();
            //}
            //catch(Exception e)
            //{
            //    Console.WriteLine(e.ToString());
            //}
                
            // Signal stopped state
            //_isrunning = false;
        }

        public static void AcceptCallback(IAsyncResult ar)
        {
            // Signal the main thread to continue.
            allDone.Set();

            if (_isrunning == false) return;

            // Get the socket that handles the client request.
            Socket listener = (Socket)ar.AsyncState;
            Socket handler = listener.EndAccept(ar);

            // Create the state object.
            StateObject state = new StateObject();
            state.workSocket = handler;
            handler.BeginReceive(state.buffer, 0, StateObject.BufferSize, 0,
                new AsyncCallback(ReadCallback), state);
        }

        public static void ReadCallback(IAsyncResult ar)
        {
            String content = String.Empty;

            // Retrieve the state object and the handler socket
            // from the asynchronous state object.
            StateObject state = (StateObject)ar.AsyncState;
            Socket handler = state.workSocket;

            // Read data from the client socket. 
            int bytesRead = handler.EndReceive(ar);

            if (bytesRead > 0)
            {
                // There  might be more data, so store the data received so far.
                state.sb.Append(Encoding.ASCII.GetString(
                    state.buffer, 0, bytesRead));

                // Check for end-of-file tag. If it is not there, read 
                // more data.
                content = state.sb.ToString();
                if (content.IndexOf("<EOF>") > -1)
                {
                    // All the data has been read from the 
                    // client. Display it on the console.
                    Console.WriteLine("Read {0} bytes from socket. \n Data : {1}",
                        content.Length, content);

                    // Analyze client message and call corresponding response handler
                    // POSSIBLE RESPONSE HANDLERS
                    // 1. hello message -> connect back (create a new client, allow only one connection at a time)
                    // 2. request to read brick data -> retrieve data, send back (TODO FIRST)
                    // 3. request to execute method -> call method with associated parameters (TODO SECOND)
                    // 4. [related to 1.] send data to client upon brick changed event

                    HandleMessage(handler, content);

                    // Echo the data back to the client.
                    //Send(handler, response); // TODO: this might not be required
                }
                else
                {
                    // Not all data received. Get more.
                    handler.BeginReceive(state.buffer, 0, StateObject.BufferSize, 0,
                    new AsyncCallback(ReadCallback), state);
                }
            }
        }

        private static void Send(Socket handler, String data)
        {
            // Convert the string data to byte data using ASCII encoding.
            byte[] byteData = Encoding.ASCII.GetBytes(data);

            // Begin sending the data to the remote device.
            handler.BeginSend(byteData, 0, byteData.Length, 0,
                new AsyncCallback(SendCallback), handler);
        }

        public static void HandleMessage(Socket handler, String s)
        {
            // create key-value pairs
            s = s.Replace("<EOF>", "").Replace("\n", ";").Replace(" ","");
            var keyValuePairs = s.Split(';')
                .Select(x => x.Split(':'))
                .Where(x => x.Length == 2)
                .ToDictionary(x => x.First(), x => x.Last());

            // function name
            string fname;

            // keyValuePairs.ContainsKey("device_type")

            if (keyValuePairs.TryGetValue("function_name", out fname))
            {
                // 
                if (fname == "get_inputport()")
                {
                    HandleGetInputPort(handler, keyValuePairs);
                }
                else if (fname == "set_inputport()")
                {
                    HandleSetInputPort(handler, keyValuePairs);
                }
                else if (fname == "set_outputport()")
                {
                    HandleSetOutputPort( handler, keyValuePairs );
                }
                else if (fname == "set_module()")
                {
                    HandleSetModule( handler, keyValuePairs );
                }
            }
        }

        public static void HandleGetInputPort(Socket handler, Message keyValuePairs)
        {
            // create response message
            String response = IComm.CreateResponse_GetInputPort( _brick, keyValuePairs );

            // send the response back to client
            Send(handler, response);
        }

        public static void HandleSetInputPort(Socket handler, Message keyValuePairs)
        {
            // set port mode
            String response = IComm.CreateResponse_SetInputPort( _brick, keyValuePairs );

            // send the response back to client
            Send(handler, response);
        }

        public static void HandleSetOutputPort(Socket handler, Message keyValuePairs)
        {
            // handle motor ports
            IComm.CreateResponse_SetOutputPort( _brick, keyValuePairs );

            // send the response back to client
            Send(handler, "message_info : callback_setoutputport()\n<EOF>");
        }

        public static void HandleSetModule(Socket handler, Message keyValuePairs)
        {
            // handle motor ports
            IComm.CreateResponse_HandleSetModule( _brick, keyValuePairs );

            // send the response back to client
            Send(handler, "message_info : callback_setmodule()\n<EOF>");
        }

        private static void SendCallback(IAsyncResult ar)
        {
            try
            {
                // Retrieve the socket from the state object.
                Socket handler = (Socket)ar.AsyncState;

                // Complete sending the data to the remote device.
                int bytesSent = handler.EndSend(ar);
                Console.WriteLine("Sent {0} bytes to client.", bytesSent);

                handler.Shutdown(SocketShutdown.Both);
                handler.Close();

            }
            catch (Exception e)
            {
                Console.WriteLine(e.ToString());
            }
        }

        public static string GetLocalIPv4(NetworkInterfaceType _type)
        {
            // Read local ip address
            string output = "";
            foreach (NetworkInterface item in NetworkInterface.GetAllNetworkInterfaces())
            {
                if (item.NetworkInterfaceType == _type && item.OperationalStatus == OperationalStatus.Up)
                {
                    foreach (UnicastIPAddressInformation ip in item.GetIPProperties().UnicastAddresses)
                    {
                        if (ip.Address.AddressFamily == AddressFamily.InterNetwork)
                        {
                            output = ip.Address.ToString();
                        }
                    }
                }
            }
            return output;
        }

        public static IPAddress LocalIPAddress()
        {
            if (!System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable())
            {
                return null;
            }

            IPHostEntry host = Dns.GetHostEntry(Dns.GetHostName());

            return host
                .AddressList
                .FirstOrDefault(ip => ip.AddressFamily == AddressFamily.InterNetwork);
        }

        public static void Start()
        {
            StartListening();
        }

        public static void Stop()
        {
            _isrunning = false;
            listener.Close();
        }
    }
} // namespace