-- Steal An Egg - Worlds Teleport Hub
local Players = game:GetService("Players")
local CoreGui = game:GetService("CoreGui")
local LocalPlayer = Players.LocalPlayer

if CoreGui:FindFirstChild("EggHubGui") then
    CoreGui.EggHubGui:Destroy()
end

local ScreenGui = Instance.new("ScreenGui")
ScreenGui.Name = "EggHubGui"
pcall(function() ScreenGui.Parent = CoreGui end)
if not ScreenGui.Parent then ScreenGui.Parent = LocalPlayer:WaitForChild("PlayerGui") end
ScreenGui.ResetOnSpawn = false

local MainFrame = Instance.new("Frame")
MainFrame.Parent = ScreenGui
MainFrame.BackgroundColor3 = Color3.fromRGB(20, 20, 25)
MainFrame.Position = UDim2.new(0.3, 0, 0.15, 0)
MainFrame.Size = UDim2.new(0, 260, 0, 420)
MainFrame.Active = true
MainFrame.Draggable = true

local Title = Instance.new("TextLabel")
Title.Parent = MainFrame
Title.BackgroundColor3 = Color3.fromRGB(10, 10, 15)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Text = "Worlds Teleport Hub 🚀"
Title.TextColor3 = Color3.fromRGB(255, 255, 255)
Title.TextSize = 16
Title.Font = Enum.Font.SourceSansBold

-- زر منطقة الأمان
local SpawnBtn = Instance.new("TextButton")
SpawnBtn.Parent = MainFrame
SpawnBtn.BackgroundColor3 = Color3.fromRGB(50, 120, 200)
SpawnBtn.Position = UDim2.new(0.1, 0, 0.12, 0)
SpawnBtn.Size = UDim2.new(0.8, 0, 0, 35)
SpawnBtn.Text = "منطقة البداية / الأمان 🛡️"
SpawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
SpawnBtn.TextSize = 14
SpawnBtn.Font = Enum.Font.SourceSansBold

SpawnBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("HumanoidRootPart") then
        local spawn = workspace:FindFirstChild("SpawnLocation") or workspace:FindFirstChild("Spawn")
        if spawn then
            char.HumanoidRootPart.CFrame = spawn.CFrame + Vector3.new(0, 3, 0)
        else
            char.HumanoidRootPart.CFrame = CFrame.new(0, 10, 0)
        end
    end
end)

-- قائمة عوالم الماب الحقيقية التي ظهرت في الصور
local worlds = {
    "Enchanted Forest",
    "Demons",
    "Titan Temple",
    "Cherry Blossom",
    "Cosmic",
    "Prehistoric",
    "Abyss Ocean",
    "Volcano",
    "Snow",
    "Jungle"
}

local selectedWorld = worlds[1]

-- زر القائمة المنسدلة لاختيار العالم
local DropdownBtn = Instance.new("TextButton")
DropdownBtn.Parent = MainFrame
DropdownBtn.BackgroundColor3 = Color3.fromRGB(35, 35, 45)
DropdownBtn.Position = UDim2.new(0.1, 0, 0.32, 0)
DropdownBtn.Size = UDim2.new(0.8, 0, 0, 35)
DropdownBtn.Text = selectedWorld .. " ▼"
DropdownBtn.TextColor3 = Color3.fromRGB(0, 255, 150)
DropdownBtn.TextSize = 14
DropdownBtn.Font = Enum.Font.SourceSansBold

-- إطار خيارات القائمة
local DropdownList = Instance.new("ScrollingFrame")
DropdownList.Parent = MainFrame
DropdownList.BackgroundColor3 = Color3.fromRGB(28, 28, 38)
DropdownList.Position = UDim2.new(0.1, 0, 0.42, 0)
DropdownList.Size = UDim2.new(0.8, 0, 0, 130)
DropdownList.Visible = false
DropdownList.CanvasSize = UDim2.new(0, 0, 2.5, 0)
DropdownList.ScrollBarThickness = 5

local UIListLayout = Instance.new("UIListLayout")
UIListLayout.Parent = DropdownList
UIListLayout.SortOrder = Enum.SortOrder.LayoutOrder

for _, worldName in ipairs(worlds) do
    local opt = Instance.new("TextButton")
    opt.Parent = DropdownList
    opt.Size = UDim2.new(1, 0, 0, 30)
    opt.BackgroundColor3 = Color3.fromRGB(40, 40, 50)
    opt.Text = worldName
    opt.TextColor3 = Color3.fromRGB(255, 255, 255)
    opt.TextSize = 13
    opt.Font = Enum.Font.SourceSans
    
    opt.MouseButton1Click:Connect(function()
        selectedWorld = worldName
        DropdownBtn.Text = worldName .. " ▼"
        DropdownList.Visible = false
    end)
end

DropdownBtn.MouseButton1Click:Connect(function()
    DropdownList.Visible = not DropdownList.Visible
end)

-- زر الانتقال للعالم المحدد
local TeleportWorldBtn = Instance.new("TextButton")
TeleportWorldBtn.Parent = MainFrame
TeleportWorldBtn.BackgroundColor3 = Color3.fromRGB(80, 180, 80)
TeleportWorldBtn.Position = UDim2.new(0.1, 0, 0.76, 0)
TeleportWorldBtn.Size = UDim2.new(0.8, 0, 0, 40)
TeleportWorldBtn.Text = "الانتقال للعالم المختار ⚡"
TeleportWorldBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
TeleportWorldBtn.TextSize = 14
TeleportWorldBtn.Font = Enum.Font.SourceSansBold

TeleportWorldBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if not char or not char:FindFirstChild("HumanoidRootPart") then return end
    local root = char.HumanoidRootPart
    
    local foundPart = nil
    for _, obj in ipairs(workspace:GetDescendants()) do
        if obj.Name == selectedWorld or (obj:IsA("TextLabel") and obj.Text == selectedWorld) then
            if obj:IsA("Model") and obj.PrimaryPart then
                foundPart = obj.PrimaryPart
                break
            elseif obj:IsA("BasePart") then
                foundPart = obj
                break
            elseif obj.Parent and obj.Parent:IsA("BasePart") then
                foundPart = obj.Parent
                break
            end
        end
    end
    
    if foundPart then
        root.CFrame = foundPart.CFrame + Vector3.new(0, 3, 0)
    end
end)

-- زر إعادة التوليد
local RespawnBtn = Instance.new("TextButton")
RespawnBtn.Parent = MainFrame
RespawnBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
RespawnBtn.Position = UDim2.new(0.1, 0, 0.89, 0)
RespawnBtn.Size = UDim2.new(0.8, 0, 0, 32)
RespawnBtn.Text = "إعادة توليد (Respawn) 🔄"
RespawnBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
RespawnBtn.TextSize = 13
RespawnBtn.Font = Enum.Font.SourceSansBold

RespawnBtn.MouseButton1Click:Connect(function()
    local char = LocalPlayer.Character
    if char and char:FindFirstChild("Humanoid") then
        char.Humanoid.Health = 0
    end
end)
