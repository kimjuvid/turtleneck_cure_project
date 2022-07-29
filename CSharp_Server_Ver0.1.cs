using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using System.Net;
using System.Net.Sockets;
using System.Threading;
using MySql.Data.MySqlClient;


namespace Sock_console_server
{

    class Receiver
    {
        public string[] select_login(string id, string pw)
        {
            string[] sql_result = new string[2];
            string c_str = "Server=127.0.0.1;Database=NECK;Uid=root;Pwd=1234;";
            string sql = $"SELECT ID, PW FROM NECK.MEMBER WHERE ID = '{id}' AND PW = '{pw}';";

            MySqlConnection conn = new MySqlConnection(c_str);
            MySqlCommand cmd = conn.CreateCommand();
            cmd.CommandText = sql;
            conn.Open();
            MySqlDataReader reader = cmd.ExecuteReader();

            while (reader.Read())
            {
                //lb_temp.Text = reader.GetString(0);
                sql_result[0] = reader.GetString(0);
                sql_result[1] = reader.GetString(1);
            }
            conn.Close();
            return sql_result;
        }



        NetworkStream NS = null;
        StreamReader SR = null;
        StreamWriter SW = null;
        TcpClient client;

        public void startClient(TcpClient clientSocket)
        {
            client = clientSocket;
            Thread echo_thread = new Thread(echo_csharp);
            echo_thread.Start();
        }



        public void echo_csharp()
        {
            NS = client.GetStream();
            // 소켓에서 메시지를 가져오는 스트림
            SR = new StreamReader(NS, Encoding.UTF8); // Get message
            SW = new StreamWriter(NS, Encoding.UTF8); // Send message
            string GetMessage = string.Empty;

            try
            {
                while (client.Connected == true) //클라이언트 메시지받기
                {
                    GetMessage = SR.ReadLine();
                    bool tf = GetMessage.Contains('$');

                    // 로그인 처리
                    if (tf == true)
                    {
                        string[] msg_split = GetMessage.Split('$');
                        Console.WriteLine("$ 스플릿 후 : " + msg_split[1]);
                        string[] id_pw = msg_split[1].Split('/');
                        Console.WriteLine($"ID : {id_pw[0]}, PW : {id_pw[1]}");
                        // 서버 DB에서 ID, PW SELECT
                        string[] sql_result = select_login(id_pw[0], id_pw[1]);
                        Console.WriteLine($"로그인 결과(RESULT) : {sql_result[0]}, {sql_result[1]}");
                        if (id_pw[0] == sql_result[0] && id_pw[0] == sql_result[0])
                        {
                            Console.WriteLine("C# 클라이언트 - 로그인 되었습니다.");
                        }
                        // 메시지에 echo를 문자를 붙힌다.
                        SW.WriteLine("Server: ID : {0} / PW : {1} [{2}]", id_pw[0], id_pw[1], DateTime.Now); // 메시지 보내기
                        SW.Flush();
                        Console.WriteLine("Log: ID : {0} / PW : {1} [{2}]", id_pw[0], id_pw[1], DateTime.Now);
                    }


                    //SW.WriteLine("Server: {0} [{1}]", GetMessage, DateTime.Now); // 메시지 보내기
                    //SW.Flush();
                    //Console.WriteLine("Log: {0} [{1}]", GetMessage, DateTime.Now);
                }
            }
            catch (Exception ee)
            {
            }
            finally
            {
                SW.Close();
                SR.Close();
                client.Close();
                NS.Close();
            }
        }


        


        // 아직 안쓰는 스레드 (startClient 복사한 거)
        public void startClient2(TcpClient clientSocket)
        {
            client = clientSocket;
            Thread echo_thread = new Thread(echo_py);
            echo_thread.Start();
        }

        // 파이썬 클라이언트 에코 받는 함수
        public void echo_py()
        {
            // server 소켓을 생성한다.
            using (var server = new Socket(AddressFamily.InterNetwork, SocketType.Stream, ProtocolType.Tcp))
            {
                // ip는 로컬이고 포트는 9999로 listen 대기한다.
                server.Bind(new IPEndPoint(IPAddress.Any, 9999));
                server.Listen(20);

                Console.WriteLine("Server Start... Listen port 9999...");

                try
                {
                    while (true)
                    {
                        // 다중 접속을 허용하기 위해 Threadpool를 이용한 멀티 쓰레드 환경을 만들었다.
                        ThreadPool.QueueUserWorkItem(c =>
                        {
                            Socket client = (Socket)c;
                            try
                            {
                                // 무한 루프로 메시지를 대기한다.
                                while (true)
                                {
                                    // 처음에 데이터 길이를 받기 위한 4byte를 선언한다.
                                    var data = new byte[4];
                                    // python에서 little 엔디언으로 값이 온다. big엔디언과 little엔디언은 배열의 순서가 반대이므로 reverse한다.
                                    client.Receive(data, 4, SocketFlags.None);
                                    Array.Reverse(data);
                                    // 데이터의 길이만큼 byte 배열을 생성한다.
                                    data = new byte[BitConverter.ToInt32(data, 0)];
                                    // 데이터를 수신한다.
                                    client.Receive(data, data.Length, SocketFlags.None);
                                    // byte를 UTF8인코딩으로 string 형식으로 변환한다.
                                    var msg = Encoding.UTF8.GetString(data);
                                    // 데이터를 콘솔에 출력한다.
                                    Console.WriteLine(msg);

                                    // 로그인 처리
                                    bool tf = msg.Contains('$');
                                    if (tf == true)
                                    {
                                        string[] msg_split = msg.Split('$');
                                        Console.WriteLine("$ 스플릿 후 : " + msg_split[1]);
                                        string[] id_pw = msg_split[1].Split('/');
                                        Console.WriteLine($"ID : {id_pw[0]}, PW : {id_pw[1]}");
                                        // 서버 DB에서 ID, PW SELECT
                                        string[] sql_result = select_login(id_pw[0], id_pw[1]);
                                        Console.WriteLine($"로그인 결과(RESULT) : {sql_result[0]}, {sql_result[1]}");
                                        if (id_pw[0] == sql_result[0] && id_pw[0] == sql_result[0])
                                        {
                                            Console.WriteLine("PYTHON 클라이언트 - 로그인 되었습니다.");
                                        }
                                        Console.WriteLine("ID : ", sql_result[0], "PW : ", sql_result[1]);
                                        // 메시지에 echo를 문자를 붙인다.
                                        msg = $"C# server : RESULT ID : {sql_result[0]} / RESULT PW : {sql_result[1]}";
                                        // 데이터를 UTF8인코딩으로 byte형식으로 변환한다.
                                        data = Encoding.UTF8.GetBytes(msg);
                                        // 데이터 길이를 클라이언트로 전송한다.
                                        client.Send(BitConverter.GetBytes(data.Length));
                                        // 데이터를 전송한다.
                                        client.Send(data, data.Length, SocketFlags.None);

                                        msg = "PYTHON Client - Login Access";
                                        // 데이터를 UTF8인코딩으로 byte형식으로 변환한다.
                                        data = Encoding.UTF8.GetBytes(msg);
                                        // 데이터 길이를 클라이언트로 전송한다.
                                        client.Send(BitConverter.GetBytes(data.Length));
                                        // 데이터를 전송한다.
                                        client.Send(data, data.Length, SocketFlags.None);
                                    }


                                    // 메시지에 echo를 문자를 붙힌다.
                                    //msg = "C# server echo : " + msg;
                                    // 데이터를 UTF8인코딩으로 byte형식으로 변환한다.
                                    //data = Encoding.UTF8.GetBytes(msg);
                                    // 데이터 길이를 클라이언트로 전송한다.
                                    //client.Send(BitConverter.GetBytes(data.Length));
                                    // 데이터를 전송한다.
                                    //client.Send(data, data.Length, SocketFlags.None);
                                }
                            }
                            catch (Exception)
                            {
                                // Exception이 발생하면 (예기치 못한 접속 종료) client socket을 닫는다.
                                client.Close();
                            }
                            // server로 client가 접속이 되면 ThreadPool에 Thread가 생성됩니다.
                        }, server.Accept());
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine(e);
                }
            }
            Console.WriteLine("Press any key...");
            Console.ReadLine();
        }
    }


    class Program
    {
        static void Main(string[] args)
        {
            TcpListener Listener = null;
            TcpClient client = null;

            int PORT = 5555;

            Console.WriteLine("서버소켓");
            try
            {
                Listener = new TcpListener(PORT);
                Listener.Start(); // Listener 동작 시작

                while (true)
                {
                    client = Listener.AcceptTcpClient();
                    Receiver r = new Receiver();
                    r.startClient(client);
                    r.echo_py();
                }
            }
            catch (Exception e)
            {
                System.Console.WriteLine(e.Message);
            }

        }
    }
}
