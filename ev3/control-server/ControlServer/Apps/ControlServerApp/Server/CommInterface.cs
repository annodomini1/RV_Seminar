using System;
using System.Reflection;
using System.ComponentModel;
//using System.Net;
//using System.Net.Sockets;
//using System.Text;
//using System.Threading;
//using System.Linq;

using Lego.Ev3.Core;
//using Lego.Ev3.Desktop;

using Message = System.Collections.Generic.Dictionary<string, string>;

namespace Server.CommInterface
{

    public class ValueReader
    {
        private Message _keyValuePairs;

        public ValueReader( Message keyValuePairs )
        {
            _keyValuePairs = keyValuePairs;
        }

        public bool GetValue( String key, bool defvalue )
        {
            try
            {
                String value;

                if ( _keyValuePairs.TryGetValue(key, out value) )
                {
                    return Convert.ToBoolean(value);
                }

                return defvalue;
            }
            catch( FormatException )
            {
                return defvalue;
            }               
        }

        public byte GetValue( String key, byte defvalue )
        {
            try
            {
                String value;

                if ( _keyValuePairs.TryGetValue(key, out value) )
                {
                    return Convert.ToByte(value);
                }

                return defvalue;
            }
            catch( FormatException )
            {
                return defvalue;
            }               
        }

        public int GetValue( String key, int defvalue )
        {
            try
            {
                String value;

                if ( _keyValuePairs.TryGetValue(key, out value) )
                {
                    return Convert.ToInt32(value);
                }

                return defvalue;
            }
            catch( FormatException )
            {
                return defvalue;
            }   
        }

        public uint GetValue( String key, uint defvalue )
        {
            try
            {
                String value;

                if ( _keyValuePairs.TryGetValue(key, out value) )
                {
                    return Convert.ToUInt32(value);
                }

                return defvalue;
            }
            catch( FormatException )
            {
                return defvalue;
            }   
        }

        public String GetValue( String key, String defvalue )
        {
            String value;

            if ( _keyValuePairs.TryGetValue(key, out value) )
            {
                return value;
            }

            return defvalue;
        }
    }


    public class IComm
    {
        private static bool IsValidBrick( Brick _brick, ref String response )
        {
            // reply with brick error if brick not initialized
            if ( _brick == null )
            {
                // add port value
                response += AddKeyValuePair("error", "Brick not initialized.");
                response += "<EOF>";                    
                return false;
            }                

            return true;
        }

        private static TEnum GetDefaultValue<TEnum>() where TEnum : struct
        {
            Type t = typeof(TEnum);
            DefaultValueAttribute[] attributes = 
                (DefaultValueAttribute[])t
                .GetCustomAttributes(
                typeof(DefaultValueAttribute), false);
            if (attributes != null &&
                attributes.Length > 0)
            {
                return (TEnum)attributes[0].Value;
            }
            else
            {
                return default(TEnum);
            }
        }

        private static TEnum GetEnumValue<TEnum>(String enum_string, out bool is_default) where TEnum : struct
        {
            // set default value
            //Array values = Array.IndexOf( Enum.GetValues(typeof(TEnum) ), 0);
            //enum_value = default(TEnum);
            TEnum enum_value = GetDefaultValue<TEnum>();
            is_default = true;

	        try
	        {
	            enum_value = (TEnum) Enum.Parse( typeof(TEnum), enum_string, true );
	        }
	        catch (Exception ex)
	        {
	            // The conversion failed.
	            Console.WriteLine(ex.Message);

	            return enum_value;
	        }

            is_default = false;

            return enum_value;
        }

        private static String AddKeyValuePair(String key, String value)
        {
            return key + ":" + value + "\n";
        }

        private static bool GetBrickInputPort( String port_letter, out InputPort BrickPort )
        {
            // make default assignment
            BrickPort = InputPort.A;

            // assign enum corresponding to brick port number
            switch ( port_letter.ToLower() )
            {
                case "a": BrickPort = InputPort.A; break;
                case "b": BrickPort = InputPort.B; break;
                case "c": BrickPort = InputPort.C; break;
                case "d": BrickPort = InputPort.D; break;

                case "1": BrickPort = InputPort.One; break;
                case "2": BrickPort = InputPort.Two; break;
                case "3": BrickPort = InputPort.Three; break;
                case "4": BrickPort = InputPort.Four; break;

                default:
                    // report error
                    return false;
            }

            return true;
        }

        private static bool GetBrickOutputPort( String port_letter, out OutputPort BrickPort )
        {
            // make default assignment
            BrickPort = OutputPort.A;

            // assign enum corresponding to brick port number
            switch ( port_letter.ToLower() )
            {
                case "a": BrickPort = OutputPort.A; break;
                case "b": BrickPort = OutputPort.B; break;
                case "c": BrickPort = OutputPort.C; break;
                case "d": BrickPort = OutputPort.D; break;

                case "ab": BrickPort = OutputPort.A | OutputPort.B; break;
                case "ac": BrickPort = OutputPort.A | OutputPort.C; break;
                case "ad": BrickPort = OutputPort.A | OutputPort.D; break;
                case "bc": BrickPort = OutputPort.B | OutputPort.C; break;
                case "bd": BrickPort = OutputPort.B | OutputPort.D; break;
                case "cd": BrickPort = OutputPort.C | OutputPort.D; break;

                case "all": BrickPort = OutputPort.All; break;

                default:
                    // report error
                    return false;
            }

            return true;
        }

        public static String CreateResponse_GetInputPort(Brick _brick, Message keyValuePairs)
        {
            String response = AddKeyValuePair("message_info", "callback_getinputport()");
            
            InputPort BrickPort;
            ValueReader VR = new ValueReader( keyValuePairs );

            if ( ! IsValidBrick( _brick, ref response ))
                return response;

            // assign enum corresponding to brick port number
            if ( ! GetBrickInputPort( VR.GetValue( "port_index", "index_error"), out BrickPort ) )
            {
                // add port value
                response += AddKeyValuePair("error", "Port index error.");
                response += "<EOF>";
                return response;
            }

            // add port index
            response += AddKeyValuePair("port_index", BrickPort.ToString());
            // add device type
            response += AddKeyValuePair("device_type", _brick.Ports[BrickPort].Type.ToString());
            // add device name
            //response += AddKeyValuePair("device_name", _brick.Ports[BrickPort].Name.ToString());
            // add device mode
            response += AddKeyValuePair("device_mode", _brick.Ports[BrickPort].Mode.ToString());
            // add values
            response += AddKeyValuePair("raw_value", _brick.Ports[BrickPort].RawValue.ToString());
            response += AddKeyValuePair("sivalue_value", _brick.Ports[BrickPort].SIValue.ToString());
            response += AddKeyValuePair("percentage_value", _brick.Ports[BrickPort].PercentValue.ToString());
            // end end-of-file tag
            response += "<EOF>";

            return response;
        }

       public static String CreateResponse_SetInputPort( Brick _brick, Message keyValuePairs )
        {
            String response = AddKeyValuePair("message_info", "callback_setinputport()");

            if ( ! IsValidBrick( _brick, ref response ))
                return response;

            ValueReader VR = new ValueReader( keyValuePairs );
            
            InputPort brickport;
            byte mode_byte;

            // assign enum corresponding to brick port index
            if ( ! GetBrickInputPort( VR.GetValue( "port_index", "index_error"), out brickport ) )
            {
                // add port value
                response += AddKeyValuePair("error", "Port index error.");
                response += "<EOF>";
                return response;
            }                  
                    
            // read params
            mode_byte = VR.GetValue( "device_mode", (byte) 0xff );

            if ( mode_byte == 0xff )
            {
                // add port value
                response += AddKeyValuePair("error", "Missing 'device_type' parameter.");
                response += "<EOF>";
                return response;
            }
            
            // set mode
            _brick.Ports[brickport].SetMode( mode_byte );

            response += "<EOF>";
            return response;
        }

        //public static String CreateResponse_SetInputPort( Brick _brick, Message keyValuePairs )
        //{
        //    String response = AddKeyValuePair("message_info", "callback_setinputport()");

        //    if ( ! IsValidBrick( _brick, ref response ))
        //        return response;

        //    ValueReader VR = new ValueReader( keyValuePairs );
            
        //    InputPort brickport;
        //    String mode_string;

        //    // assign enum corresponding to brick port index
        //    if ( ! GetBrickInputPort( VR.GetValue( "port_index", "index_error"), out brickport ) )
        //    {
        //        // add port value
        //        response += AddKeyValuePair("error", "Port index error.");
        //        response += "<EOF>";
        //        return response;
        //    }                  
                    
        //    // read params
        //    mode_string = VR.GetValue( "device_mode", "unknown");

        //    if ( mode_string == "unknown" )
        //    {
        //        // add port value
        //        response += AddKeyValuePair("error", "Missing 'device_type' parameter.");
        //        response += "<EOF>";
        //        return response;
        //    }     

        //    // get enum type
        //    Type enumtype = _brick.Ports[brickport].Mode.GetType(); // THIS IS ALWAYS byte!
        //    var enum_value = Activator.CreateInstance(enumtype);
        //    bool is_default = false;

        //    // create method for enum type
        //    MethodInfo method = typeof(IComm).GetMethod( "GetEnumValue", 
        //        BindingFlags.NonPublic | BindingFlags.Static );
        //    MethodInfo generic = method.MakeGenericMethod( enumtype );

        //    //  invoke method using given parameters
        //    object[] args = new object[] { mode_string, is_default };
        //    enum_value = generic.Invoke( null, args );                       
        //    is_default = (bool) args[1];
            
        //    if ( is_default )
        //    {
        //        // add port value
        //        response += AddKeyValuePair("warning", "Cannot resolve mode - setting to default.");
        //    }   
            
        //    // set mode
        //    _brick.Ports[brickport].SetMode( (dynamic) enum_value );

        //    response += "<EOF>";
        //    return response;
        //}

        public async static void CreateResponse_SetOutputPort( Brick _brick, Message keyValuePairs )
        {            
            String response = AddKeyValuePair("message_info", "callback_setoutputport()");

            if ( ! IsValidBrick( _brick, ref response ))
                return;
                //return response;

            ValueReader VR = new ValueReader( keyValuePairs );

            OutputPort brickport, brickport2;
            int power, power2;
            uint steps, time, steps2, time2;
            bool brake, brake2;

            // assign enum corresponding to brick port index
            if ( ! GetBrickOutputPort( VR.GetValue( "port_index", "index_error"), out brickport ) )
                return;
            //{
            //    // add port value
            //    response += AddKeyValuePair("error", "Port index error.");
            //    response += "<EOF>";
            //    return response;
            //}    
                    
            // read params
            power = VR.GetValue( "power", 0);
            steps = VR.GetValue( "steps", (uint) 0);
            time = VR.GetValue( "time_ms", (uint) 0);
            brake = VR.GetValue( "brake", false);

            power2 = VR.GetValue( "power2", 0);
            steps2 = VR.GetValue( "steps2", (uint) 0);
            time2 = VR.GetValue( "time_ms2", (uint) 0);
            brake2 = VR.GetValue( "brake2", false);

            switch ( VR.GetValue("motor_fname", "fname_error()") )
            {
                case "StepMotorAtPowerAsync()":
                    
                    // execute command
                    await _brick.DirectCommand.StepMotorAtPowerAsync(brickport, power, 0, steps, 0, brake);

                    break;

                case "TurnMotorAtPowerAsync()":

                    // execute command
                    await _brick.DirectCommand.TurnMotorAtPowerAsync(brickport, power);

                    break;

                case "TurnMotorAtPowerForTimeAsync()":
                    
                    // execute command
                    await _brick.DirectCommand.TurnMotorAtPowerForTimeAsync(brickport, power, 0, time, 0, brake);

                    break;

                case "StopMotorAsync()":

                    // execute command
                    await _brick.DirectCommand.StopMotorAsync(brickport, brake);

                    break;
                
                case "StepMotorAtPowerBatch()":

                    // assign enum corresponding to brick port index
                    if ( ! GetBrickOutputPort( VR.GetValue( "port_index2", "index_error"), out brickport2 ) )
                        break;
                    //{
                    //    // add port value
                    //    response += AddKeyValuePair("error", "Port index 2 error.");
                    //    break;
                    //}

                    // execute command
                    _brick.BatchCommand.StepMotorAtPower(brickport, power, 0, steps, 0, brake);
                    _brick.BatchCommand.StepMotorAtPower(brickport2, power2, 0, steps2, 0, brake2);
                    
                    await _brick.BatchCommand.SendCommandAsync();

                    break;

                case "TurnMotorAtPowerBatch()":
                    
                    // assign enum corresponding to brick port index
                    if ( ! GetBrickOutputPort( VR.GetValue( "port_index2", "index_error"), out brickport2 ) )
                        break;
                    //{
                    //    // add port value
                    //    response += AddKeyValuePair("error", "Port index 2 error.");
                    //    break;
                    //}

                    // execute command
                    _brick.BatchCommand.TurnMotorAtPower(brickport, power);
                    _brick.BatchCommand.TurnMotorAtPower(brickport2, power2);

                    await _brick.BatchCommand.SendCommandAsync();

                    break;

                case "TurnMotorAtPowerForTimeBatch()":
                    
                    // assign enum corresponding to brick port index
                    if ( ! GetBrickOutputPort( VR.GetValue( "port_index2", "index_error"), out brickport2 ) )
                        break;
                    //{
                    //    // add port value
                    //    response += AddKeyValuePair("error", "Port index 2 error.");
                    //    break;
                    //}                        
                    
                    // execute command
                    _brick.BatchCommand.TurnMotorAtPowerForTime(brickport, power, 0, time, 0, brake);
                    _brick.BatchCommand.TurnMotorAtPowerForTime(brickport2, power2, 0, time2, 0, brake2);

                    await _brick.BatchCommand.SendCommandAsync();

                    break;
            }

            //// close response message
            //response += "<EOF>";
            //return response;
        }


        public async static void CreateResponse_HandleSetModule(Brick _brick, Message keyValuePairs)
        {
            String response = AddKeyValuePair("message_info", "callback_setoutputport()");

            if (!IsValidBrick(_brick, ref response))
                return;

            ValueReader VR = new ValueReader( keyValuePairs );

            int volume = VR.GetValue("volume", 100);

            switch (VR.GetValue("module_fname", "fname_error()"))
            {
                case "PlayToneAsync()":
                    
                    uint frequency = VR.GetValue("frequency", (uint) 1000);
                    uint duration = VR.GetValue("duration_ms", (uint) 1000);

                    // execute command
                    await _brick.DirectCommand.PlayToneAsync(volume, (ushort) frequency, (ushort) duration);

                    break;

                case "PlaySoundAsync()":

                    String filename = VR.GetValue("filename", "");

                    await _brick.DirectCommand.PlaySoundAsync(volume, filename);

                    break;

                case "CleanUIAsync()":

                    await _brick.DirectCommand.CleanUIAsync();

                    break;

                case "ClearChangesAsync()":

                    InputPort brickport;

                    // assign enum corresponding to brick port number
                    if ( ! GetBrickInputPort( VR.GetValue( "port_index", "index_error"), out brickport ) )
                        break;

                    await _brick.DirectCommand.ClearChangesAsync( brickport );

                    break;

                case "ClearAllDevicesAsync()":

                    await _brick.DirectCommand.ClearAllDevicesAsync();

                    break;

                case "SetLedPatternAsync()":

                    int ledpattern = VR.GetValue("ledpattern", 0);

                    await _brick.DirectCommand.SetLedPatternAsync( (LedPattern) ledpattern );

                    break;
            }
        }
    }
} 