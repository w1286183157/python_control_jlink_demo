<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>WebUSB J-Link Burner</title>
</head>
<body>
<button onclick="connectJLink()">Connect to JLink</button>
<button onclick="burnFirmware()">Burn Firmware</button>
<script>
    let jlinkDevice;
    const filters = [{vendorId: 0x1366}];

    async function connectJLink() {
        var usbDevice;
        try {
            usbDevice = await navigator.usb.requestDevice({filters: []});
            // Connect to the USB Device and open it for our use
            await usbDevice.open();
            console.log("usbDevice", usbDevice);
            const usbInterface = usbDevice.configuration?.interfaces[0];
            if (usbInterface === undefined) {
                console.log("Failed to connect, failed to find usbInterface");
                return;
            }
            //开启两个端口 in out
            const inEndpoint = usbInterface.alternate.endpoints.find(
                (e) => e.direction === "in"
            );
            const outEndpoint = usbInterface.alternate.endpoints.find(
                (e) => e.direction === "out"
            );
            await usbDevice.claimInterface(usbInterface.interfaceNumber);

            const EMU_CMD_VERSION = 1;
            await usbDevice.transferOut(
                outEndpoint.endpointNumber,
                new Uint8Array([EMU_CMD_VERSION])
            );
            const versionInLength = await usbDevice.transferIn(
                inEndpoint.endpointNumber,
                0x02 // number of bytes of length
            );
            const length = versionInLength.data?.getUint16(0, true);
            console.log(length);

            const versionIn = await usbDevice.transferIn(
                inEndpoint.endpointNumber,
                length
            );
            var firmwareVersion = new TextDecoder()
                .decode(versionIn.data)
                .replaceAll("\0", "\n");

            console.log(firmwareVersion)

        } catch (error) {
            console.error(error);
        }
    }

    async function programDevice() {
        const jlinkExePath = 'C:\\Program Files\\SEGGER\\JLink\\JLink.exe';
        const scriptPath = 'D:\\Coding\\PycharmProjects\\JLinkProgramTool\\script.jlink';
        const command = `${jlinkExePath} -Device N32G031C8L7 -If SWD -Speed 1000 -CommanderScript ${scriptPath}`;
        const options = {shell: true};
        await navigator.usb.transferOut(0x02, new Uint8Array([0x00])); // JLink start mode
        const process = await Deno.run({cmd: command, stdout: "piped", stderr: "piped", ...options});
        const [stdout, stderr] = await Promise.all([process.output(), process.stderrOutput()]);
        console.log(new TextDecoder().decode(stdout));
        await navigator.usb.transferOut(0x02, new Uint8Array([0x01])); // JLink reset mode
    }

    async function burnFirmware() {
        await programDevice();
    }

</script>

</body>
</html>
