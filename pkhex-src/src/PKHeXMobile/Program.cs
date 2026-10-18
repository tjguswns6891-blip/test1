using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using PKHeX.Core;
using PKHeXMobile;
using PKHeXMobile.Services;

// The browser runtime has no AES; Gen 7 saves need it to re-sign on export.
RuntimeCryptographyProvider.Aes = new ManagedAesProvider();

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");

builder.Services.AddSingleton<AppState>();

await builder.Build().RunAsync();
