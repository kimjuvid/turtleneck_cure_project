using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.IO;
using System.Net;
using System.Net.Sockets;

namespace ConsoleTest
{
    class Program
    {
        static void Main(string[] args)
        {
            int PORT = 5555;
            string IP = "localhost";

            NetworkStream NS = null;
            StreamReader SR = null;
            StreamWriter SW = null;
            TcpClient client = null;

            try
            {
                client = new TcpClient(IP, PORT); //client 연결
                Console.WriteLine("{0}:{1}에 접속하였습니다.", IP, PORT);
                NS = client.GetStream(); // 소켓에서 메시지를 가져오는 스트림
                SR = new StreamReader(NS, Encoding.UTF8); // Get message
                SW = new StreamWriter(NS, Encoding.UTF8); // Send message

                string SendMessage = string.Empty;
                string GetMessage = string.Empty;

                while ((SendMessage = Console.ReadLine()) != null)
                {

                    SW.WriteLine(SendMessage); // 메시지 보내기
                    SW.Flush();

                    GetMessage = SR.ReadLine();
                    Console.WriteLine(GetMessage);
                }
            }

            catch (Exception e)
            {
                System.Console.WriteLine(e.Message);
            }
            finally
            {
                if (SW != null) SW.Close();
                if (SR != null) SR.Close();
                if (client != null) client.Close();
            }
        }
    }
}
